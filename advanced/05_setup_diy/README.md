# Goal
Effective development needs an effective Developer-setup. Unfortunately that's for a crosscompiled microcotroller-project much more fifficult to achieve then for a web-based-project. But we'll try to make the best out of it.
The ways on how to get an effective Feed-back cycle for a developer is, depending on the specific use-case, much more complex.
We can distinguish:
* Download the firmware from somewhere or compile it yourself and deploy on hardware via Mini-USB (just for the reference, this is what's described in the Readme.md)
* Deploy an empty micropython-project and directly deploy the code on the device and then change files directly on the device
* Compile the micropython_unixport and start the simulator.
* Run the tests

# Direct Device Editing
It would be a security-issue if the default deployment of specter on the device would allow code-editing directly on the device. Therefore the deployment-process which will eventually allow that, is a bit different.
For details see [Micropython without frozen firmware](https://github.com/cryptoadvance/specter-diy#micropython-without-frozen-firmware)

# Run the Simulator
Compile the unixport and start the simulator. This is easily done via:
```
./specter.sh builddeps
./specter.sh sim
```
More about that can be found in the [Simulator-section](https://github.com/cryptoadvance/specter-diy#simulator)

# Run the tests
```
./specter.sh tests
```
