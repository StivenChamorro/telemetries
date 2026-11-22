<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('telemetries', function (Blueprint $table) {
            $table->id();
           // --- Producción (Panel Solar - ACS712 y FZ0430) ---
            $table->float('solar_voltage');     // Voltaje del panel (V)
            $table->float('solar_current');     // Corriente del panel (A)
            $table->float('solar_power');       // Potencia de producción (W)

            // --- Consumo (11 LEDs - INA219) ---
            $table->float('load_voltage');      // Voltaje de carga de los LEDs (V)
            $table->float('load_current');      // Corriente de consumo (A)
            $table->float('load_power');        // Potencia de consumo (W)
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('telemetries');
    }
};
