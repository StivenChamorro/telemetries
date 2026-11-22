<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

return new class extends Migration {
    public function up(): void {
        // Agregar los nuevos campos de producción y consumo solo si no existen
        Schema::table('telemetries', function (Blueprint $table) {
            if (!Schema::hasColumn('telemetries', 'solar_voltage')) {
                $table->decimal('solar_voltage', 8, 2)->nullable();
                $table->decimal('solar_current', 8, 2)->nullable();
                $table->decimal('solar_power', 8, 2)->nullable();
                $table->decimal('load_voltage', 8, 2)->nullable();
                $table->decimal('load_current', 8, 2)->nullable();
                $table->decimal('load_power', 8, 2)->nullable();
            }
        });

        // Crear la tabla de configuración si no existe
        if (!Schema::hasTable('system_settings')) {
            Schema::create('system_settings', function (Blueprint $table) {
                $table->id();
                $table->string('key')->unique();
                $table->string('value');
                $table->timestamps();
            });

            DB::table('system_settings')->insert([
                'key' => 'system_status',
                'value' => 'ON',
                'created_at' => now(),
                'updated_at' => now()
            ]);
        }
    }

    public function down(): void {
        Schema::dropIfExists('system_settings');
        
        Schema::table('telemetries', function (Blueprint $table) {
            $table->dropColumn([
                'solar_voltage', 
                'solar_current', 
                'solar_power', 
                'load_voltage', 
                'load_current', 
                'load_power'
            ]);
        });
    }
};