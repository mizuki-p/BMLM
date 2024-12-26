# Boundless Multi-Modal Large Model (BMLM)

## Introduction

**A Unified Framework: Data-Driven, Knowledge-Guided, Mechanism-Constrained**  

The Boundless Multi-Modal Large Model (BMLM) is a cutting-edge framework designed to enable autonomous perception, planning, decision-making, and behavior execution across diverse spaces, tasks, and ontologies.  

### **Spatial Unboundedness**  
BMLM seamlessly integrates data from the digital, physical, and social realms. It processes virtual data from digital environments, real-time sensory input from the physical world, and interactive information from social contexts to operate across boundaries.  

### **Task Unboundedness**  
BMLM transcends task limitations by supporting dynamic adaptation and intelligent decision-making in complex multitasking scenarios, delivering flexible and efficient performance.  

### **Ontological Unboundedness**  
BMLM fosters cross-ontology knowledge transfer and reasoning, enabling intelligent coordination and reasoning across diverse domains and ontological structures.  

---

## Demo  

⚠ **Note:** Currently, the demo supports only the **Windows** operating system.  

The demo consists of three main components:  
1. **Model**: Deployed on a cloud server.  
2. **AirSim Simulator**: Developed by Microsoft.  
3. **Graphical User Interface (GUI)**: For interactive control and visualization.  

Download the AirSim simulator [here](https://drive.google.com/file/d/11_w8nvnTiNiJdulGBy5rW6tlH5KCmoQ7/view?usp=sharing).  

### Getting Started  

#### Step 1: Set Up Python Environment  
We recommend using Miniconda to create a virtual environment, but other tools can also be used.  

1. Clone the repository:  
   ```powershell
   git clone https://github.com/mizuki-p/BMLM.git
   ```  

2. Navigate to the repository and create a virtual environment:  
   ```powershell
   cd BMLM
   conda create -n bmlm python=3.10 -y
   conda activate bmlm
   ```  

3. Install the required Python packages:  
   ```powershell
   pip install -r requirements.txt
   ```  

#### Step 2: Launch the AirSim Simulator  
1. Open a terminal in the root directory of your AirSim installation.  
2. Start the simulator by running:  
   ```powershell
   .\Blocks.exe -settings=.\settings.json
   ```  
   If prompted to install the .NET environment, follow the instructions provided.  

#### Step 3: Start the GUI Client  
1. Activate the Python environment within the repository:  
   ```powershell
   conda activate bmlm
   ```  

2. Navigate to the `client` directory and run the example script:  
   ```powershell
   cd client
   python .\example\airsim_example.py
   ```  
   This will start a local web server.  

3. Open a browser and visit [http://localhost:33601](http://localhost:33601) to access the GUI.  

#### Step 4: Interact with the Demo  
1. **Register the Model**: Click **Register** to connect the Model to the system.  
2. **Start Video**: Click **Start Video** to stream the vehicle's camera feed.  
3. **Send Instructions**: Enter your commands in the input field and click **Execute**. The Model will interpret your instructions, generate Python code, and send it to the AirSim simulator for execution.  

Explore the capabilities of BMLM and see it in action!  
