import 'dart:async';
import 'package:sqflite/sqflite.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import 'package:connectivity_plus/connectivity_plus.dart';

import 'api_client.dart';
import 'hash_capture.dart';

/// The institutes most likely to need surprise inspection are often in
/// low-connectivity districts - the same places a naive "always-online"
/// app breaks first. Every capture is hashed and queued to a local
/// SQLite table FIRST, independent of network state; a background sync
/// drains the queue the moment connectivity returns. Nothing about
/// capture or hashing ever waits on a network call.
class OfflineQueue {
  OfflineQueue(this._api);

  final ApiClient _api;
  Database? _db;

  Future<Database> get _database async {
    if (_db != null) return _db!;
    final dir = await getApplicationDocumentsDirectory();
    final path = p.join(dir.path, 'evidence_queue.db');
    _db = await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) => db.execute('''
        CREATE TABLE queue (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          assignment_id TEXT NOT NULL,
          file_path TEXT NOT NULL,
          sha256_hash TEXT NOT NULL,
          gps_lat REAL NOT NULL,
          gps_lng REAL NOT NULL,
          device_id TEXT NOT NULL,
          captured_at TEXT NOT NULL,
          synced INTEGER NOT NULL DEFAULT 0
        )
      '''),
    );
    return _db!;
  }

  /// Called right after capture - hashing already happened in
  /// hash_capture.dart before this is ever invoked, so what's queued is
  /// already the tamper-evident record, not raw unhashed bytes.
  Future<void> enqueue({
    required String assignmentId,
    required CapturedEvidence evidence,
    required double gpsLat,
    required double gpsLng,
    required String deviceId,
  }) async {
    final db = await _database;
    await db.insert('queue', {
      'assignment_id': assignmentId,
      'file_path': evidence.filePath,
      'sha256_hash': evidence.sha256Hash,
      'gps_lat': gpsLat,
      'gps_lng': gpsLng,
      'device_id': deviceId,
      'captured_at': evidence.capturedAt.toIso8601String(),
      'synced': 0,
    });
  }

  Future<int> pendingCount() async {
    final db = await _database;
    final result = await db.rawQuery('SELECT COUNT(*) as c FROM queue WHERE synced = 0');
    return Sqflite.firstIntValue(result) ?? 0;
  }

  /// Drains every unsynced row, in capture order, stopping cleanly on the
  /// first upload failure (network drop mid-sync) rather than losing
  /// track of what's left - the remaining rows stay queued for the next
  /// connectivity window.
  Future<int> syncPending() async {
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) return 0;

    final db = await _database;
    final rows = await db.query('queue', where: 'synced = 0', orderBy: 'id ASC');

    var syncedCount = 0;
    for (final row in rows) {
      try {
        await _api.uploadEvidence(
          assignmentId: row['assignment_id'] as String,
          filePath: row['file_path'] as String,
          clientHash: row['sha256_hash'] as String,
          gpsLat: row['gps_lat'] as double,
          gpsLng: row['gps_lng'] as double,
          deviceId: row['device_id'] as String,
        );
        await db.update('queue', {'synced': 1}, where: 'id = ?', whereArgs: [row['id']]);
        syncedCount++;
      } catch (_) {
        break; // stop here - preserves order, retries this row first next time
      }
    }
    return syncedCount;
  }
}
