import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:provider/provider.dart';

import '../models/assignment.dart';
import '../services/api_client.dart';
import '../services/offline_queue.dart';
import 'capture_screen.dart';

class InspectorHomeScreen extends StatefulWidget {
  const InspectorHomeScreen({super.key});

  @override
  State<InspectorHomeScreen> createState() => _InspectorHomeScreenState();
}

class _InspectorHomeScreenState extends State<InspectorHomeScreen> {
  Assignment? _assignment;
  bool _loading = true;
  int _pendingSync = 0;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final api = context.read<ApiClient>();
      final json = await api.myAssignment();
      final queue = context.read<OfflineQueue>();
      final pending = await queue.pendingCount();
      setState(() {
        _assignment = json != null ? Assignment.fromJson(json) : null;
        _pendingSync = pending;
      });
    } catch (e) {
      setState(() => _error = 'Could not load your assignment');
    } finally {
      setState(() => _loading = false);
    }
  }

  Future<void> _sendGeofencePing() async {
    if (_assignment == null) return;
    try {
      final position = await Geolocator.getCurrentPosition();
      final api = context.read<ApiClient>();
      final updated = await api.geofencePing(_assignment!.id, position.latitude, position.longitude);
      setState(() => _assignment = Assignment.fromJson(updated));
      if (mounted) {
        final triggered = Assignment.fromJson(updated).isGeofenceTriggered;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              triggered
                  ? 'Within range - institute has now been notified'
                  : 'Not yet within the geofence radius',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Could not check location')));
      }
    }
  }

  Future<void> _syncNow() async {
    final queue = context.read<OfflineQueue>();
    final synced = await queue.syncPending();
    final remaining = await queue.pendingCount();
    setState(() => _pendingSync = remaining);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Synced $synced item(s) - $remaining still pending')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My assignment')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
                  if (_assignment == null)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(16),
                        child: Text('No assignment yet. Pull to refresh once one is generated.'),
                      ),
                    )
                  else ...[
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Assignment ${_assignment!.id.substring(0, 8)}',
                                style: const TextStyle(fontWeight: FontWeight.w600)),
                            const SizedBox(height: 4),
                            Text(_assignment!.isGeofenceTriggered
                                ? 'Institute has been notified - proceed to capture evidence'
                                : 'Institute has NOT been notified yet - move into range and check in'),
                            const SizedBox(height: 12),
                            if (!_assignment!.isGeofenceTriggered)
                              FilledButton(onPressed: _sendGeofencePing, child: const Text('Check location')),
                            if (_assignment!.isGeofenceTriggered)
                              FilledButton(
                                onPressed: () => Navigator.of(context).push(
                                  MaterialPageRoute(
                                    builder: (_) => CaptureScreen(assignmentId: _assignment!.id),
                                  ),
                                ),
                                child: const Text('Capture evidence'),
                              ),
                          ],
                        ),
                      ),
                    ),
                  ],
                  const SizedBox(height: 16),
                  Card(
                    color: _pendingSync > 0 ? Colors.amber.shade50 : null,
                    child: ListTile(
                      title: Text('$_pendingSync item(s) waiting to sync'),
                      subtitle: const Text('Captured offline - queued locally, hashed already'),
                      trailing: TextButton(onPressed: _syncNow, child: const Text('Sync now')),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
