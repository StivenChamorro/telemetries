<?php

use Illuminate\Http\Request;
use App\Http\Controllers\TelemetryController;
use Illuminate\Support\Facades\Route;


//Route::get('/user', function (Request $request) {
//  return $request->user();
///})->middleware('auth:sanctum');

Route::post('/telemetry', [TelemetryController::class, 'store']);
Route::get('/telemetry', [TelemetryController::class, 'index']);
Route::get('/telemetry/latest', [TelemetryController::class, 'latest']);
Route::get('/system/status', [TelemetryController::class, 'getSystemStatus']);
Route::post('/system/toggle', [TelemetryController::class, 'toggleSystemStatus']);