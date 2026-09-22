import 'dart:io';
import 'package:crypto/crypto.dart';

/// Computes SHA-256 of a captured file's bytes IMMEDIATELY after capture,
/// before the file is queued, touched, or uploaded. This is what the
/// server independently re-verifies in evidence/upload - see
/// backend/app/services/hashing.py. If these two hashes ever disagree,
/// the file was altered somewhere between here and the server, and the
/// upload is rejected outright.
class HashCapture {
  static Future<String> sha256OfFile(String filePath) async {
    final bytes = await File(filePath).readAsBytes();
    return sha256.convert(bytes).toString();
  }

  static Future<CapturedEvidence> hashImmediatelyAfterCapture(String filePath) async {
    final capturedAt = DateTime.now().toUtc();
    final hash = await sha256OfFile(filePath);
    return CapturedEvidence(filePath: filePath, sha256Hash: hash, capturedAt: capturedAt);
  }
}

class CapturedEvidence {
  CapturedEvidence({required this.filePath, required this.sha256Hash, required this.capturedAt});
  final String filePath;
  final String sha256Hash;
  final DateTime capturedAt;
}
