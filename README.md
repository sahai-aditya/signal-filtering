# Signal Filtering: From Synthetic Noise to the MPU-6050

A hands-on comparison of four classic digital filters (**First-Order Low-Pass**, **Moving Average**, **Complementary**, and **Kalman**), first on a noisy synthetic sine wave and then on real-time data from an **MPU-6050 IMU**.



## Project Roadmap

|Phase|Description|Status|
|-|-|-|
|1|Generate noisy synthetic sine data|✅ Done|
|2|Implement first-order low-pass filter|⬜ Planned|
|3|Implement moving average filter|⬜ Planned|
|4|Implement complementary filter|⬜ Planned|
|5|Implement 1D Kalman filter|⬜ Planned|
|6|Compare all filters (noise, lag, and more)|⬜ Planned|
|7|Apply filters to real-time MPU-6050 data|⬜ Planned|
|8|Compile results into `results/results.pdf`|⬜ Planned|



## Phase Descriptions

**Phase 1: Synthetic Data Generation**
Generate a clean sine wave as ground truth. Add Gaussian noise using a fixed random seed, so every filter is tested on identical data.

**Phase 2: First-Order Low-Pass Filter**
Smooth the noisy signal with exponential smoothing. Study how the smoothing factor α trades noise suppression against lag.

**Phase 3: Moving Average Filter**
Average the last N samples. Observe how the window size affects smoothness and delay.

**Phase 4: Complementary Filter**
Fuse two simulated sources with complementary noise behaviour: a noisy "accelerometer" signal and a biased, noisy "gyroscope" rate signal.

**Phase 5: Kalman Filter**
Implement a 1D Kalman filter. Tune the process noise (Q) and measurement noise (R) to balance smoothness and responsiveness.

**Phase 6: Filter Comparison**
Run all filters on the same data and evaluate each one using the metrics below. Then plot the results side by side with Matplotlib.

**Phase 7: MPU-6050 Real-Time Filtering**
Read live accelerometer and gyroscope data from the MPU-6050 over I²C. Apply the filters to estimate tilt angles, and plot raw vs filtered data in real time.

**Phase 8: Results Report**
Compile all graphs, metric tables, and observations from the synthetic and real-sensor tests into `results/results.pdf`.



## Comparison Metrics

|Metric|What it measures|
|-|-|
|**Noise (RMSE)**|Overall error between the filtered signal and the true signal|
|**Lag**|Time delay introduced by the filter, measured from the peak of the cross-correlation|
|**Noise reduction ratio / SNR gain**|How much noise is removed, measured independently of lag|
|**Amplitude attenuation**|How much the filter shrinks the signal's peaks|
|**Step response**|Rise time, settling time, and overshoot after a sudden change|
|**Frequency response**|Attenuation and phase lag across a range of frequencies|
|**Drift / bias rejection**|Error growth over time when the gyroscope has a constant bias|
|**Computational cost**|Time per sample and memory used (relevant for microcontrollers)|
|**Parameter sensitivity**|How performance changes as α, N, β, Q, and R are varied|



## Author

**Aditya Sahai**, M.Sc. Physics + B.E. Mechanical Engineering, BITS Pilani



