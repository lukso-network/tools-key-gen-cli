import pytest
import sys
import json
from typing import (
    Any,
)

from ethstaker_deposit.exceptions import ValidationError
from ethstaker_deposit.settings import get_chain_setting, get_devnet_chain_setting
from ethstaker_deposit.utils.validation import (
    normalize_input_list,
    validate_int_range,
    validate_deposit_amount,
    validate_password_strength,
    validate_signed_exit,
    validate_devnet_chain_setting_json,
)


@pytest.mark.parametrize(
    'password, valid',
    [
        ('MyPasswordIs', True),
        ('MyPassword', False),
    ]
)
def test_validate_password_strength(password: str, valid: bool) -> None:
    if valid:
        validate_password_strength(password=password)
    else:
        with pytest.raises(ValidationError):
            validate_password_strength(password=password)


@pytest.mark.parametrize(
    'password, encoding, platform, valid',
    [
        ('Surströmming', 'utf-8', 'linux', True),
        ('Surströmming', 'latin-1', 'linux', False),
        ('Surstromming', 'latin-1', 'linux', True),
        ('Surströmming', 'utf-8', 'darwin', True),
        ('Surströmming', 'latin-1', 'darwin', False),
        ('Surstromming', 'latin-1', 'darwin', True),
        ('Surströmming', 'utf-8', 'win32', True),
        ('Surströmming', 'latin-1', 'win32', False),
        ('Surstromming', 'latin-1', 'win32', True),
    ]
)
def test_validate_password_strength_encoding(
    monkeypatch, password: str, encoding: str, platform: str, valid: bool
) -> None:
    class MockStdin:
        def __init__(self, encoding):
            self.encoding = encoding
    mock_stdin = MockStdin(encoding=encoding)
    monkeypatch.setattr(sys, 'stdin', mock_stdin)
    monkeypatch.setattr(sys, 'platform', platform)

    if valid:
        validate_password_strength(password=password)
    else:
        with pytest.raises(ValidationError):
            validate_password_strength(password=password)


@pytest.mark.parametrize(
    'num, low, high, valid',
    [
        (2, 0, 4, True),
        (0, 0, 4, True),
        (-1, 0, 4, False),
        (4, 0, 4, False),
        (0.2, 0, 4, False),
        ('0', 0, 4, True),
        ('a', 0, 4, False),
    ]
)
def test_validate_int_range(num: Any, low: int, high: int, valid: bool) -> None:
    if valid:
        validate_int_range(num, low, high)
    else:
        with pytest.raises(ValidationError):
            validate_int_range(num, low, high)


@pytest.mark.parametrize(
    'amount, valid, chain',
    [
        ('-1', False, 'mainnet'),
        ('0', False, 'mainnet'),
        ('0.99999', False, 'mainnet'),
        ('0.99999', True, 'gnosis'),
        ('0.99999', True, 'chiado'),
        ('0.99999', False, 'devnet'),
        ('1', True, 'mainnet'),
        ('1.000000001', True, 'mainnet'),
        ('1.0000000001', False, 'mainnet'),
        ('1', False, 'devnet'),
        ('32', True, 'mainnet'),
        ('32', True, 'gnosis'),
        ('32', True, 'chiado'),
        ('32', True, 'devnet'),
        ('2048', True, 'mainnet'),
        ('2048', False, 'gnosis'),
        ('2048', False, 'chiado'),
        ('2048', False, 'devnet'),
        ('2048.000000001', False, 'mainnet'),
        ('2048.0000000001', False, 'mainnet'),
        ('a', False, 'mainnet'),
        ('a', False, 'gnosis'),
        ('a', False, 'chiado'),
        ('a', False, 'devnet'),
        (' ', False, 'mainnet')
    ]
)
def test_validate_deposit_amount(amount: str, valid: bool, chain: str) -> None:
    if chain == 'devnet':
        kwargs = {'params': {'devnet_chain_setting': get_devnet_chain_setting(
        "devnet",
        "01017000",
        "04017000",
        "9143aa7c615a7f7115e2b6aac319c03529df8242ae705fba9df39b79c59fa8b1",
        5,
        3,
        2,
    )}}
    else:
        kwargs = {'params': {'chain': chain}}
    if valid:
        validate_deposit_amount(amount, **kwargs)
    else:
        with pytest.raises(ValidationError):
            validate_deposit_amount(amount, **kwargs)


@pytest.mark.parametrize(
    'input, result',
    [
        ('1', ['1']),
        ('1,2,3', ['1', '2', '3']),
        ('[1,2,3]', ['1', '2', '3']),
        ('(1,2,3)', ['1', '2', '3']),
        ('{1,2,3}', ['1', '2', '3']),
        ('1 2 3', ['1', '2', '3']),
        ('1  2  3', ['1', '2', '3']),
    ]
)
def test_normalize_input_list(input, result):
    assert normalize_input_list(input) == result


valid_pubkey = "911e7c7fc980bcf5400980917ee92797d52d226768e1b26985fabaf5f214464059ab2d52170b0605f4c8e7a872cde436"
valid_signature = (
    "0x854053a7faebf4547ca3904ff14d896a994d5fb7289478681842fb72622364cd0cb4922170a370ea53234a734b47cd6"
    "80c7edca86e8d796abd8eaeb8dd85d99e57c962c84d6642dff4b6e9bfb6d6df5fa22910c583f13135f5b2b43e4f95e8cf"
)
invalid_pubkey = "b54186e3dbdde180cc39f52e0cf4207c5745a50e2e8bd12f49b925f87682cab88ef108f60cf3ea1ac82b7c6fe796f5d6"
invalid_signature = (
    "0x8cceb99d17361031e01dfb6aa997554a35f60bcc8a106ac76fdea6f5a4780fb8b65b4cd827bca0c88b340508b69f577"
    "50122db94c319aa05a0165e71b41f30c0982c415727b7e2387cce78d995acd54f038b743dc1426b0fb0d4783617d4fe6e"
)


@pytest.mark.parametrize(
    'chain, epoch, validator_index, pubkey, signature, result',
    [
        # valid
        ('mainnet', 0, 0, valid_pubkey, valid_signature, True),
        # bad chain
        ('hoodi', 0, 0, valid_pubkey, valid_signature, False),
        # bad epoch
        ('mainnet', 1, 0, valid_pubkey, valid_signature, False),
        # bad validator_index
        ('mainnet', 0, 1, valid_pubkey, valid_signature, False),
        # bad pubkey
        ('mainnet', 0, 0, invalid_pubkey, valid_signature, False),
        # bad signature
        ('mainnet', 0, 0, valid_pubkey, invalid_signature, False),
    ]
)
def test_validate_signed_exit(
    chain: str, epoch: int, validator_index: int, pubkey: str, signature: str, result: bool
) -> None:
    chain_setting = get_chain_setting(chain)

    assert validate_signed_exit(validator_index, epoch, signature, pubkey, chain_setting) == result


def test_validate_devnet_chain_setting_json() -> None:
    # Correct devnet chain value
    corret_devnet_chain = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000",
        "genesis_validator_root": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f"
    }
    assert validate_devnet_chain_setting_json(json.dumps(corret_devnet_chain)) is True

    # Invalid devnet chain value missing 1 required key
    missing_1_key_devnet_chain = {
        "network_name": "hoodicopy",
        "exit_fork_version": "04017000",
        "genesis_validator_root": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f"
    }
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json(json.dumps(missing_1_key_devnet_chain)) is False

    # Invalid devnet chain value missing 2 required key
    missing_2_keys_devnet_chain = {
        "exit_fork_version": "04017000",
        "genesis_validator_root": "9143aa7c615a7f7115e2b6aac319c03529df8242ae705fba9df39b79c59fa8b1"
    }
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json(json.dumps(missing_2_keys_devnet_chain)) is False

    # Correct devnet chain value missing 1 optional key
    correct_missing_genesis_validator_root_devnet_chain = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000"
    }
    assert validate_devnet_chain_setting_json(json.dumps(correct_missing_genesis_validator_root_devnet_chain)) is True

    # Invalid devnet chain value with wrong fourth key name
    invalid_fourth_key_devnet_chain = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000",
        "genesis_validator": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f"
    }
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json(json.dumps(invalid_fourth_key_devnet_chain)) is False

    # Invalid devnet chain value with too many keys
    invalid_too_many_keys_devnet_chain = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000",
        "genesis_validator_root": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f",
        "multiplier": "1",
        "min_deposit_amount": "1",
        "more_key": "value"
    }
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json(json.dumps(invalid_too_many_keys_devnet_chain)) is False

    # Invalid devnet chain with invalid JSON string
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json('aaz') is False

    # Invalid devnet chain with missing root JSON object
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json('[1, 2, 3]') is False

    correct_devnet_chain_with_multiplier = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000",
        "genesis_validator_root": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f",
        "multiplier": "1"
    }
    assert validate_devnet_chain_setting_json(json.dumps(correct_devnet_chain_with_multiplier)) is True

    correct_devnet_chain_with_multiplier_and_min_deposit_amount = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000",
        "genesis_validator_root": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f",
        "multiplier": "1",
        "min_deposit_amount": "1"
    }
    assert validate_devnet_chain_setting_json(
        json.dumps(correct_devnet_chain_with_multiplier_and_min_deposit_amount)) is True

    invalid_devnet_chain_with_min_deposit_amount_and_wrong_key = {
        "network_name": "hoodicopy",
        "genesis_fork_version": "10000910",
        "exit_fork_version": "04017000",
        "genesis_validator_root": "212f13fc4df078b6cb7db228f1c8307566dcecf900867401a92023d7ba99cb5f",
        "min_deposit_amount": "1",
        "compounding": "true"
    }
    with pytest.raises(ValidationError):
        assert validate_devnet_chain_setting_json(
            json.dumps(invalid_devnet_chain_with_min_deposit_amount_and_wrong_key)) is False
