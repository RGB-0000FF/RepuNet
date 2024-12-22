# Setting up the environments 

To set up your environment, you will need to generate a `utils.py` file that contains your OpenAI API key and download the necessary packages.



### Step 1. Generate Utils File

In the initial folder (where `start.py` is located), create a new file titled `utils.py` and copy and paste the content below into the file:

```python
# Copy and paste your OpenAI API Key
openai_api_key = <Your OpenAI API>
# Put your name
key_owner = <name>

fs_storage = './sim_storage'

```

Replace `<Your OpenAI API>` with your OpenAI API key, and `<name>` with your name.



### Step 2. Install requirements.txt

Install everything listed in the `requirements.txt` file (I strongly recommend first setting up a virtualenv as usual). A  note on Python version: we tested our environment on Python 3.9.



### Step 3. create a simulation seed

Create a folder for your simulation inside `sim_storage`. The simulation folder should follow the format `sim_storage/<your_simulation>` (e.g., `sim_storage/investment_s1`).

Within your simulation folder, create a subfolder named `step_0` (e.g., `sim_storage/investment_s1/step_0`). The `step_0` folder serves as the **seed** for the simulation, containing the initial configuration, input data, or state required to begin the simulation process.

Next, open the `change_sim_folder.py` script and update the following:

- Replace `base_folder = "sim_storage/<your_sim_folder>"` with the path to your simulation folder.
- Customize the `persona_descriptions` variable to match the specific requirements of your simulation.

This setup initializes the simulation and prepares it to generate subsequent steps based on the defined starting conditions in `step_0`.



It is important to note that your `step_0` folder needs to contain two subfolders:

1. **`personas`**: This can be empty, as it will be initialized by `change_sim_folder.py`.

2. **`reverie`**: This folder must include a `meta.json` file with the following format:

   ```python
   {
     "persona_names": [
       "name1",
       "name2",
       "name3"
     ],
     "step": 0
   }
   
   ```





# Running a Simulation

Run `start.py` in your terminal.

When prompted with `Enter the name of the forked simulation:`, input the path to your simulation folder and step, in the format `<your_sim_folder>/step_<step>`.

- For example: `investment_s1/step_0`.









