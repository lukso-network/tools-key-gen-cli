# existing-mnemonic

{{#include ./snippet/warning_message.md}}

## Description
Uses an existing BIP-39 mnemonic phrase for key generation.

## Optional Arguments

- **`--chain`**: The chain to use for generating the deposit data. Options are: 'mainnet', 'sepolia', 'holesky', 'hoodi', 'ephemery', 'gnosis', 'chiado', 'lukso' or 'lukso-testnet'.

- **`--mnemonic`**: The mnemonic you used to create withdrawal credentials. <span class="warning"></span>

- **`--mnemonic_language`**: The language of your mnemonic. If this is not provided we will attempt to determine it based on the mnemonic.

- **`--mnemonic_password`**: The mnemonic password you used in your key generation. Note: It's not the keystore password. <span class="warning"></span>

- **`--validator_start_index`**: The index of the first validator's keys you wish to generate. If this is your first time generating keys with this mnemonic, use 0. If you have generated keys using this mnemonic before, use the next index from which you want to start generating keys from. As an example if you've generated 4 keys before (keys #0, #1, #2, #3), then enter 4 here.

- **`--num_validators`**: Number of validators to create.

- **`--keystore_password`**: The password that is used to encrypt the provided keystore. Note: It's not your mnemonic password. <span class="warning"></span>

- **`--withdrawal_address`**: The Ethereum address that will be used in withdrawal. It typically starts with '0x' followed by 40 hexadecimal characters. Please make sure you have full control over the address you choose here. Once you set a withdrawal address on chain, it cannot be changed.

- **`--compounding / --regular-withdrawal`**: Generates compounding validators with 0x02 withdrawal credentials for a 2048 ETH maximum effective balance or generate regular validators with 0x01 withdrawal credentials for a 32 ETH maximum effective balance. Use of this option requires a withdrawal address. This feature is only supported on networks that have undergone the Pectra fork. Defaults to regular withdrawal.

- **`--amount`**: The amount to deposit to these validators in ether denomination. Must be at least 1 ether and can not have greater precision than 1 gwei. Use of this option requires compounding validators. Defaults to 32 ether.

- **`--pbkdf2`**: Will use pbkdf2 key derivation instead of scrypt for generated keystore files as defined in [EIP-2335](https://eips.ethereum.org/EIPS/eip-2335#decryption-key). This can be a good alternative if you intend to work with a large number of keys, as it can improve performance however it is less secure. You should only use this option if you understand the associated risks and have familiarity with encryption.

- **`--folder`**: The folder where keystore and deposit data files will be saved.

- **`--devnet_chain_setting`**: The custom chain setting of a devnet or testnet. Note that it will override your `--chain` choice. This should be a JSON string containing an object with the following keys: network_name, genesis_fork_version, exit_fork_version, genesis_validator_root, multiplier, min_activation_amount and min_deposit_amount.

## Output files
A successful call to this command will result in one or many [keystore files](keystore_file.md) created, one per validator created, and one [deposit data file](deposit_data_file.md) created. The amount for each deposit in the deposit data file should always be 32 Ethers (`32000000000` in GWEI) with this command.

## Example Usage

```sh
./deposit existing-mnemonic
```

## Note

To make a deposit for a different amount other than 32 ETH, you need to have an existing keystore file or create one by using either the above command or **[new-mnemonic](new_mnemonic.md)**. Then, use the **[partial-deposit](partial_deposit.md)** command to specify the desired amount for each validator.
