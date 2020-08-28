import BloombergAPI_new as BloombergAPI
import pandas as pd
import numpy as np



if __name__ == "__main__":

    StartDate = 20200618
    EndDate = 20200718
    x = ["SPX Index","IBOV Index"]
    blp = BloombergAPI.BLPInterface()