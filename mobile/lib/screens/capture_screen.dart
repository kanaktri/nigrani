import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/hash_capture.dart';
import '../services/offline_queue.dart';

/// The evidence capture flow, in the exact order the report's USP2
/// requires: capture -> hash on-device IMMEDIATELY -> read GPS ->
/// enqueue locally (works with zero connectivity) -> sync when possible.
/// Nothing here waits on the network except the final sync step.
class CaptureScreen extends StatefulWidget {
  const CaptureScreen({super.key, required this.assignmentId});
  final String assignmentId;

  @override
  State<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends State<CaptureScreen> {
  bool _busy = false;
  String? _status;
  String? _lastHash;

  Future<void> _captureAndQueue() async {
    setState(() {
      _busy = true;
      _status = 'Opening camera…';
    });

    try {
      final picker = ImagePicker();
      final photo = await picker.pickImage(source: ImageSource.camera, imageQuality: 90);
      if (photo == null) {
        setState(() => _status = 'Capture cancelled');
        return;
      }

      setState(() => _status = 'Hashing on-device…');
      // Hashed HERE, immediately, before anything else touches the file -
      // this is the timestamp that matters for evidence integrity, not
      // whenever the upload eventually happens.
      final evidence = await HashCapture.hashImmediatelyAfterCapture(photo.path);

      setState(() => _status = 'Reading GPS…');
      final position = await Geolocator.getCurrentPosition();

      final prefs = await SharedPreferences.getInstance();
      final deviceId = prefs.getString('device_id') ?? await _ensureDeviceId(prefs);

      setState(() => _status = 'Queuing (works offline)…');
      final queue = context.read<OfflineQueue>();
      await queue.enqueue(
        assignmentId: widget.assignmentId,
        evidence: evidence,
        gpsLat: position.latitude,
        gpsLng: position.longitude,
        deviceId: deviceId,
      );

      setState(() {
        _lastHash = evidence.sha256Hash;
        _status = 'Queued locally. Will upload automatically once online.';
      });

      // Best-effort immediate sync if connectivity happens to be up right
      // now - but the capture is already safely queued regardless.
      await queue.syncPending();
    } catch (e) {
      setState(() => _status = 'Something went wrong: $e');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<String> _ensureDeviceId(SharedPreferences prefs) async {
    final id = DateTime.now().microsecondsSinceEpoch.toString();
    await prefs.setString('device_id', id);
    return id;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Capture evidence')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.camera_alt_outlined, size: 64),
            const SizedBox(height: 16),
            if (_status != null) Text(_status!, textAlign: TextAlign.center),
            if (_lastHash != null) ...[
              const SizedBox(height: 8),
              Text(
                'SHA-256: ${_lastHash!.substring(0, 16)}…',
                style: const TextStyle(fontFamily: 'monospace', fontSize: 12, color: Colors.black54),
              ),
            ],
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _busy ? null : _captureAndQueue,
              icon: const Icon(Icons.camera_alt),
              label: Text(_busy ? 'Working…' : 'Capture photo'),
            ),
          ],
        ),
      ),
    );
  }
}
