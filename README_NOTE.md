If you see ModuleNotFoundError: No module named 'plotly' when running the notebook:

1. Ensure the notebook uses the project's virtualenv as the kernel:
   - In Jupyter Notebook / Lab: Kernel -> Change kernel -> select "Python (nike-venv)".

2. If the kernel is not listed, register the venv as a kernel (run in terminal):
   /Users/wavy/Documents/portfolio/nike_data_analysis/venv/bin/python -m ipykernel install --user --name nike-venv --display-name "Python (nike-venv)"

3. Alternative quick fix inside notebook (installs into the current kernel):
   In a new cell at the top of the notebook, run:
   %pip install plotly

4. To recreate the environment on another machine:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

5. Verified: plotly v6.3.1 is installed in the workspace venv at ./venv and importable.
