import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'screens/login_screen.dart';
import 'services/api_client.dart';
import 'services/auth_service.dart';
import 'services/offline_queue.dart';

void main() {
  runApp(const DoSJENayanApp());
}

class DoSJENayanApp extends StatelessWidget {
  const DoSJENayanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiClient>(create: (_) => ApiClient()),
        Provider<AuthService>(create: (ctx) => AuthService(ctx.read<ApiClient>())),
        Provider<OfflineQueue>(create: (ctx) => OfflineQueue(ctx.read<ApiClient>())),
      ],
      child: MaterialApp(
        title: 'DoSJE Nayan',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorSchemeSeed: const Color(0xFF12222E),
          useMaterial3: true,
        ),
        home: const LoginScreen(),
      ),
    );
  }
}
