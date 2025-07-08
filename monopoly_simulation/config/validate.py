import yaml

def validate_config(config_path: str) -> dict:
    """
    Validates the configuration parameters for the Monopoly simulation.

    :param config_path: Path to the configuration YAML file.
    :return: Loaded and validated configuration dictionary.
    :raises ValueError: If any configuration parameter is invalid.
    """
    print(f"Validating configuration from {config_path}...")
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file) or {}

    # Required fields and their validation rules
    required_positive_ints = [
        "board_size", "die_faces", "start_cash", "max_turns"
    ]
    
    required_non_negative_ints = [
        "tax_fields", "chance_fields", "property_fields"
    ]

    required_boolean = [
        "train_agent"
    ]

    for required_fields in [required_positive_ints, required_non_negative_ints]:
        for key in required_fields:
            if key not in config:
                raise ValueError(f"Missing required configuration parameter: '{key}'")
            
    # Validate positive integers
    for key in required_positive_ints:
        value = config.get(key)
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"Invalid '{key}': must be a positive integer.")

    # Validate non-negative integers
    for key in required_non_negative_ints:
        value = config.get(key)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid '{key}': must be a non-negative integer.")

    # Validate boolean values
    for key in required_boolean:
        value = config.get(key)
        if not isinstance(value, bool):
            raise ValueError(f"Invalid '{key}': must be a boolean value.")

    # Validate that total fields do not exceed board size
    total_fields = sum(config.get(k, 0) for k in required_non_negative_ints)
    if total_fields > config["board_size"]:
        raise ValueError(
            f"The sum of fields ({total_fields}) exceeds the board size ({config['board_size']})."
        )

    # Validate chance events
    chance_events = config.get("chance_events")
    if not chance_events:
        raise ValueError("No chance events defined in the configuration.")
    for event in chance_events:
        if event["action"] not in ["move", "pay", "receive", "skip"]:
            raise ValueError(f"Invalid action '{event["action"]}' in chance events.")
        if not isinstance(event["amount"], int):
            raise ValueError(f"Invalid value '{event["amount"]}' in chance events, must an integer.")

    # Vaidate player type
    player_type = config["player_type"]
    if player_type not in ["always_buy", "qlearning", "never_buy"]:
        raise ValueError(f"Invalid player type '{player_type}'. Must be one of 'always_buy', 'qlearning', or 'never_buy'.")



    print("Configuration validation successful.")
    return config

if __name__ == "__main__":
    validate_config("default_config.yaml")