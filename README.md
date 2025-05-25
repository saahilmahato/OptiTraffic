# 🚦 Multi-Intersection Traffic Signal Simulation

This project simulates and compares two traffic signal control strategies— Fixed-Time based, and Multi-Agent Reinforcement Learning (MARL)—across multiple intersections. The goal is to evaluate their performance in managing urban traffic congestion.

---

## 📄 Research Paper

For an in-depth analysis and results, refer to the research paper:

[arXiv\:2505.14544](https://arxiv.org/abs/2505.14544)

---

## 🧪 Project Setup

### Prerequisites

* Python 3.8+
* pip (Python package installer)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/codesaahil/OptiTraffic.git
   cd OptiTraffic
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the Simulation

To execute the simulation:

```bash
python3 -m src.main
```

Optional parameter `controllerType`
By default the script will use fixed controller.
For MARL controller you can use:

```bash
python3 -m src.main --controllerType marl
```

This command initializes the simulation environment and begins the traffic signal control processes.

---

## 🧪 Running Multiple Simulations

To run a series of simulations and record various results:

```bash
./run_simulations.sh
```

This will run simulations 40 times. Each run will be for 10 minutes. The first 20 runs will be for fixed controller and the later 20 will be for MARL controller.


Ensure the script has execute permissions:

```bash
chmod +x run_simulations.sh
```



This script automates the execution of multiple simulation scenarios, capturing performance metrics for analysis.

---

## 📊 Evaluating Results

After collecting simulation data, use the following script to process records and perform hypothesis tests:

```bash
python3 evaluate.py
```



This script analyzes the recorded data, providing statistical insights into the performance of each traffic signal control strategy.

---

## 🧩 Project Structure

Here's an overview of the project's directory structure:

```plaintext
your-repo/
├── src/                  # Source code for the simulation
│   ├── main.py           # Entry point for the simulation
│   └── ...               # Additional modules
├── run_simulations.sh    # Shell script to run multiple simulations
├── evaluate.py           # Script to process results and perform analysis
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```



---

## 🧑‍💻 Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request.
