<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Telemetry extends Model
{
    use HasFactory;

    protected $fillable = [
        'solar_voltage',
        'solar_current',
        'solar_power',
        'load_voltage',
        'load_current',
        'load_power',
        ];
}
