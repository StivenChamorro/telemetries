<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Telemetry;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Carbon\Carbon;

class TelemetryController extends Controller
{
    // Guardar lecturas de la ESP32 (Panel y Carga) y responder con el estado
    public function store(Request $request)
    {
        // 1. Consultar primero el estado del sistema en la BD
        $systemStatus = DB::table('system_settings')->where('key', 'system_status')->value('value') ?? 'ON';

        // 2. Si el sistema está en OFF, NO guardamos los datos
        if ($systemStatus === 'OFF') {
            return response()->json([
                'status'        => 'system_disabled',
                'message'       => 'El sistema está apagado desde el Dashboard',
                'system_status' => 'OFF'
            ], 200);
        }

        // 3. Si el sistema está en ON, procesamos y guardamos con los nuevos campos
        $validated = $request->validate([
            'solar_voltage' => ['required', 'numeric'],
            'solar_current' => ['required', 'numeric'],
           'load_voltage'  => ['required', 'numeric'],
           'load_current'  => ['required', 'numeric'],
        ]);

        $solarPower = $validated['solar_voltage'] * $validated['solar_current'];
        $loadPower  = $validated['load_voltage'] * $validated['load_current'];

        $record = Telemetry::create([
            'solar_voltage' => $validated['solar_voltage'],
            'solar_current' => $validated['solar_current'],
            'solar_power'   => $solarPower,
            'load_voltage'  => $validated['load_voltage'],
            'load_current'  => $validated['load_current'],
            'load_power'    => $loadPower,
        ]);

        // Verificamos alertas basados en el voltaje y corriente del panel solar
        $this->checkAndSendAlerts($validated['solar_voltage'], $validated['solar_current']);

        return response()->json([
            'status'        => 'success',
            'system_status' => 'ON',
            'data'          => $record
        ], 201);
    }

    // Consultar estado actual del sistema
    public function getSystemStatus()
    {
        $status = DB::table('system_settings')->where('key', 'system_status')->value('value') ?? 'ON';
        return response()->json(['system_status' => $status]);
    }

    // Cambiar estado del sistema (Botón del Dashboard)
    public function toggleSystemStatus(Request $request)
    {
        $newStatus = $request->input('status', 'OFF');
        DB::table('system_settings')->where('key', 'system_status')->update([
            'value'      => $newStatus,
            'updated_at' => now()
        ]);

        return response()->json(['status' => 'success', 'system_status' => $newStatus]);
    }

    // Datos para el Dashboard (Lecturas actualizadas con analítica de producción y consumo)
    public function index()
    {
        $latest = Telemetry::latest()->take(25)->get();

        // Estadísticas agregadas adaptadas a las nuevas columnas
        $stats = [
            'avg_solar_voltage' => round(Telemetry::avg('solar_voltage') ?? 0, 2),
            'max_solar_voltage' => round(Telemetry::max('solar_voltage') ?? 0, 2),
            'min_solar_voltage' => round(Telemetry::min('solar_voltage') ?? 0, 2),
            'avg_solar_current' => round(Telemetry::avg('solar_current') ?? 0, 2),
            'max_solar_current' => round(Telemetry::max('solar_current') ?? 0, 2),
            'min_solar_current' => round(Telemetry::min('solar_current') ?? 0, 2),
            'avg_solar_power'   => round(Telemetry::avg('solar_power') ?? 0, 2),
            'max_solar_power'   => round(Telemetry::max('solar_power') ?? 0, 2),
            
            'avg_load_voltage'  => round(Telemetry::avg('load_voltage') ?? 0, 2),
            'avg_load_current'  => round(Telemetry::avg('load_current') ?? 0, 2),
            'avg_load_power'    => round(Telemetry::avg('load_power') ?? 0, 2),
            'max_load_power'    => round(Telemetry::max('load_power') ?? 0, 2),
            
            'total_records'     => Telemetry::count(),
        ];

        $systemStatus = DB::table('system_settings')->where('key', 'system_status')->value('value') ?? 'ON';

        return response()->json([
            'readings'      => $latest,
            'stats'         => $stats,
            'system_status' => $systemStatus
        ]);
    }

    // Envío de Alertas a WhatsApp
    private function checkAndSendAlerts($voltage, $current)
    {
        $maxVoltage = 10.5; // Umbral de alerta
        $maxCurrent = 2.0;

        if ($voltage > $maxVoltage || $current > $maxCurrent) {
            $phone = env('WHATSAPP_PHONE');
            $apiKey = env('WHATSAPP_APIKEY');

            if (!$phone || !$apiKey) {
                return;
            }

            $message = "⚠️ *ALERTA TELEMETRÍA ESP32* ⚠️\n";
            $message .= "Se han detectado valores fuera de rango en el panel:\n";
            $message .= "⚡ Voltaje Solar: {$voltage} V\n";
            $message .= "🔌 Corriente Solar: {$current} A\n";
            $message .= "📅 Fecha: " . now()->format('Y-m-d H:i:s');

            $url = "https://api.callmebot.com/whatsapp.php?phone={$phone}&text=" . urlencode($message) . "&apikey={$apiKey}";

            try {
                $response = Http::get($url);
                if ($response->successful()) {
                    Log::info("Alerta de WhatsApp enviada con éxito.");
                }
            } catch (\Exception $e) {
                Log::error("Error al enviar WhatsApp: " . $e->getMessage());
            }
        }
    }

    // Consultar el último registro en formato JSON crudo para el navegador~
    public function latest()
    {
        $ultimoDato = Telemetry::latest()->first();

        if (!$ultimoDato) {
            return response()->json([
                'message' => 'Aún no hay datos registrados por la ESP32'
            ], 404);
        }

        return response()->json($ultimoDato, 200);
    }
}