# Try the Seshat API in Jupyter

You can explore the Seshat data in an interactive Jupyter notebook. This folder contains examples of how to use it. First, follow these steps:

1. Ensure you have a working installation of Python 3 and Conda. If not, [download Anaconda](https://seshat-global-history-databank.github.io/seshat/software-tools.html#python-anaconda), which should give you both
    - Note: you can use a different tool for creating a Python virtual environment than conda (e.g. venv) if you prefer

2. Set up a virtual environment with conda.

    ```
        conda create --name seshat_api python=3.11
        conda activate seshat_api
    ```

3. Install the *seshat_api* package into the venv.

    ```     
        git clone https://github.com/Seshat-Global-History-Databank/seshat_api
        cd seshat_api
        pip install .
    ```

4. You can then open the notebook with Jupyter (or another application that can run notebooks such as VSCode). First go to this examples dir and install any packages required by the notebook into the venv, then create a kernel and finally open the Jupyter notebook application:
    ```
        cd examples
        pip install -r requirements.txt
        python -m ipykernel install --user --name=seshat_api --display-name="Python (seshat_api)"
        jupyter notebook
    ```
    - Note: if Jupyter wants to to set a password, use `Ctrl-C` to escape and run `jupyter notebook --generate-config` before running `jupyter notebook` again and entering a blank password.

5. From the Jupyter notebook interface in your browser, choose an `.ipynb` file to open, then choose the Kernel that you created called `Python (seshat_api)` in the top right.

6. Follow the instructions in the notebook.

## Additional requirements for `LLM.ipynb`

1. Download and install [Ollama](https://ollama.com/)

2. In the CLI, ensure `deepseek-r1` is installed and usable:

    ```
        ollama run deepseek-r1
    ```
