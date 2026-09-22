import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

/// Thin HTTP wrapper around the backend API. Every method mirrors one
/// endpoint from the API contract (see backend/app/api/v1/) - if the
/// backend adds or changes a route, this is the one file to update.
class ApiClient {
  ApiClient({this.baseUrl = 'http://10.0.2.2:8000/api/v1'});
  // 10.0.2.2 is the Android emulator's alias for the host machine's
  // localhost - swap for the real backend URL when pointing at a
  // deployed instance (see README "Mobile app configuration").

  final String baseUrl;

  Future<String?> _token() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token');
  }

  Future<Map<String, String>> _authHeaders() async {
    final token = await _token();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<Map<String, dynamic>> login(String email, String password) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (resp.statusCode != 200) {
      throw ApiException('Incorrect email or password');
    }
    final body = jsonDecode(resp.body) as Map<String, dynamic>;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', body['access_token'] as String);
    await prefs.setString('role', body['role'] as String);
    await prefs.setString('user_id', body['user_id'] as String);
    return body;
  }

  Future<Map<String, dynamic>?> myAssignment() async {
    final resp = await http.get(
      Uri.parse('$baseUrl/assignments/mine'),
      headers: await _authHeaders(),
    );
    if (resp.statusCode != 200) throw ApiException('Could not load assignment');
    if (resp.body == 'null' || resp.body.isEmpty) return null;
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> geofencePing(String assignmentId, double lat, double lng) async {
    final resp = await http.post(
      Uri.parse('$baseUrl/assignments/$assignmentId/geofence-ping'),
      headers: await _authHeaders(),
      body: jsonEncode({'latitude': lat, 'longitude': lng}),
    );
    if (resp.statusCode != 200) throw ApiException('Geofence ping failed');
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }

  /// Uploads evidence with its ALREADY-COMPUTED hash (see hash_capture.dart)
  /// - the server independently recomputes and compares; a mismatch is
  /// rejected outright. This method never re-hashes anything itself, so
  /// it can't accidentally mask a hash computed from stale/wrong bytes.
  Future<Map<String, dynamic>> uploadEvidence({
    required String assignmentId,
    required String filePath,
    required String clientHash,
    required double gpsLat,
    required double gpsLng,
    required String deviceId,
  }) async {
    final token = await _token();
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/evidence/upload'))
      ..headers['Authorization'] = 'Bearer $token'
      ..fields['assignment_id'] = assignmentId
      ..fields['client_hash'] = clientHash
      ..fields['gps_lat'] = gpsLat.toString()
      ..fields['gps_lng'] = gpsLng.toString()
      ..fields['device_id'] = deviceId
      ..files.add(await http.MultipartFile.fromPath('file', filePath));

    final streamed = await request.send();
    final resp = await http.Response.fromStream(streamed);
    if (resp.statusCode != 200) throw ApiException('Evidence upload failed');
    return jsonDecode(resp.body) as Map<String, dynamic>;
  }
}

class ApiException implements Exception {
  ApiException(this.message);
  final String message;
  @override
  String toString() => message;
}
