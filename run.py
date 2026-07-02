import argparse
import yaml
import numpy as np
import pandas as pd
import time
import json
import logging
import sys


def validate_config(config):
    # Required fields
    required_fields = ["seed", "window", "version"]

    # Check if all required fields exist
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field: '{field}'")

    # Validate seed
    if not isinstance(config["seed"], int):
        raise ValueError("Seed must be an integer.")

    # Validate window
    if not isinstance(config["window"], int) or config["window"] <= 0:
        raise ValueError("Window must be a positive integer.")

    # Validate version
    if not isinstance(config["version"], str):
        raise ValueError("Version must be a string.")
    
    
def validate_dataset(df):
    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError("Dataset is empty.")

    # Check if the required column exists
    if "close" not in df.columns:
        raise ValueError("Required column 'close' not found in dataset.")

    print("Dataset validation successful!")


def main():
    try:
        start_time = time.perf_counter()

        parser = argparse.ArgumentParser(description="Minimal MLOps Batch Job")

        parser.add_argument("--input", required=True)
        parser.add_argument("--config", required=True)
        parser.add_argument("--output", required=True)
        parser.add_argument("--log-file", required=True)

        args = parser.parse_args()


        logging.basicConfig(
            filename=args.log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.info("========== Job Started ==========")




        # Load YAML
        with open(args.config, "r") as file:
            config = yaml.safe_load(file)
            
            
        validate_config(config)
        logging.info("Configuration validated successfully.")

        np.random.seed(config["seed"])
        logging.info(f"Random seed set to {config['seed']}")

        # with open(args.input, "r", encoding="utf-8") as file:
        #     print(repr(file.readline()))
        # Load the dataset
        # Load dataset
        # Load dataset
        df = pd.read_csv(args.input)

        # Handle malformed CSV where each row is stored as one quoted string
        if df.shape[1] == 1:
            # Split the single column into multiple columns
            df = df.iloc[:, 0].str.split(",", expand=True)

            # Use the original header (already read by pandas)
            headers = pd.read_csv(args.input, nrows=0).columns[0].replace('"', '').split(",")

            df.columns = headers

        # Clean column names
        df.columns = df.columns.str.strip().str.lower()


        logging.info(f"Dataset loaded successfully with {len(df)} rows.")
        print(f"Rows: {len(df)}")
        validate_dataset(df)

        logging.info("Dataset validation successful.")
        print(df.shape)
        print(df.columns)
        print(df.head())

        # Convert close column to numeric
        df["close"] = pd.to_numeric(df["close"])
        # Compute rolling mean
        window = config["window"]

        df["rolling_mean"] = df["close"].rolling(
            window=window,
            min_periods=window
        ).mean()
        logging.info(f"Rolling mean computed using window={config['window']}.")
        print(df[["close", "rolling_mean"]].head(10))

        # Generate trading signal
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)
        logging.info("Trading signals generated.")
        print(df[["close", "rolling_mean", "signal"]].head(10))

        rows_processed = len(df)
        signal_rate = df["signal"].mean()
        latency_ms = round((time.perf_counter() - start_time) * 1000)
        print("\n===== Metrics =====")
        print(f"Rows Processed : {rows_processed}")
        print(f"Signal Rate    : {signal_rate:.4f}")
        print(f"Latency (ms)   : {latency_ms}")

        metrics = {
            "version": config["version"],
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": config["seed"],
            "status": "success"
        }

        logging.info(
            f"Rows={rows_processed}, "
            f"Signal Rate={signal_rate:.4f}, "
            f"Latency={latency_ms} ms"
        )

        logging.info("Metrics written successfully.")
        logging.info("========== Job Completed Successfully ==========")


        with open(args.output, "w") as file:
            json.dump(metrics, file, indent=4)
            
        print("\nFinal Metrics:")
        print(json.dumps(metrics, indent=4))

        print("\nLoaded Configuration:")
        print(config)

        print("Seed :",config["seed"])
        print("Window :", config["window"])
        print("Version :", config["version"])

        print("Input File :", args.input)
        print("Config File:", args.config)
        print("Output File:", args.output)
        print("Log File   :", args.log_file)
    except Exception as e:

        logging.exception("Job failed.")

        error_metrics = {
            "version": config["version"] if "config" in locals() and isinstance(config, dict) and "version" in config else "unknown",
            "status": "error",
            "error_message": str(e)
        }

        # Try to write metrics.json
        try:
            output_path = args.output if "args" in locals() else "metrics.json"

            with open(output_path, "w") as file:
                json.dump(error_metrics, file, indent=4)

        except Exception:
            pass

        # Print error JSON to stdout
        print(json.dumps(error_metrics, indent=4))

        sys.exit(1)
        
if __name__ == "__main__":
    main()