class Assignment {
  Assignment({
    required this.id,
    required this.instituteId,
    required this.inspectorId,
    this.geofenceTriggeredAt,
  });

  final String id;
  final String instituteId;
  final String inspectorId;
  final DateTime? geofenceTriggeredAt;

  factory Assignment.fromJson(Map<String, dynamic> json) => Assignment(
        id: json['id'] as String,
        instituteId: json['institute_id'] as String,
        inspectorId: json['inspector_id'] as String,
        geofenceTriggeredAt: json['geofence_triggered_at'] != null
            ? DateTime.parse(json['geofence_triggered_at'] as String)
            : null,
      );

  bool get isGeofenceTriggered => geofenceTriggeredAt != null;
}
