import { createClient, chains, abi } from 'genlayer-js';
import { encodeFunctionData, toRlp, toHex } from 'viem';

export const STUDIONET_CHAIN_ID_DEC = 61999;
export const STUDIONET_CHAIN_ID_HEX = "0xF22F";
export const STUDIONET_RPC_URL = "https://studio.genlayer.com/api";
export const STUDIONET_EXPLORER_URL = "https://studio.genlayer.com";

// Deployed intelligent contract on GenLayer StudioNet
export const DEFAULT_CONTRACT_ADDRESS = "0x7bb4e10087C5b80748fA46364C8b209738cC13d5";

export const genlayerClient = createClient({
  chain: chains.studionet,
});

const ADD_TRANSACTION_ABI_V5 = [
  {
    type: 'function',
    name: 'addTransaction',
    stateMutability: 'nonpayable',
    inputs: [
      { name: '_sender', type: 'address' },
      { name: '_recipient', type: 'address' },
      { name: '_numOfInitialValidators', type: 'uint256' },
      { name: '_maxRotations', type: 'uint256' },
      { name: '_txData', type: 'bytes' }
    ],
    outputs: []
  }
];

export function encodeGenLayerTransaction(
  senderAddress: string,
  recipientAddress: string,
  functionName: string,
  args: any[]
): { to: `0x${string}`; data: `0x${string}` } {
  const calldataObj = (abi.calldata as any).makeCalldataObject(functionName, args, undefined);
  const encoded = (abi.calldata as any).encode(calldataObj);
  const serialized = toRlp([toHex(encoded), toHex(0)]);
  const consensusAddress = ((chains.studionet as any).consensusMainContract?.address || "0xb7278A61aa25c888815aFC32Ad3cC52fF24fE575") as `0x${string}`;

  const data = encodeFunctionData({
    abi: ADD_TRANSACTION_ABI_V5,
    functionName: 'addTransaction',
    args: [
      senderAddress as `0x${string}`,
      recipientAddress as `0x${string}`,
      5n,
      3n,
      serialized as `0x${string}`
    ]
  });

  return {
    to: consensusAddress,
    data
  };
}

export const STUDIONET_CHAIN_CONFIG = {
  chainId: STUDIONET_CHAIN_ID_HEX,
  chainName: "GenLayer StudioNet",
  nativeCurrency: {
    name: "GEN",
    symbol: "GEN",
    decimals: 18,
  },
  rpcUrls: [STUDIONET_RPC_URL],
  blockExplorerUrls: [STUDIONET_EXPLORER_URL],
};

export const CONTRACT_ABI = [
  {
    name: "register_warranty_vault",
    type: "function",
    inputs: [
      { name: "consumer_address", type: "Address" },
      { name: "device_serial_or_vin", type: "string" },
      { name: "firmware_version", type: "string" },
      { name: "warranty_blocks", type: "int" },
    ],
    outputs: [{ name: "vault_id", type: "u64" }],
  },
  {
    name: "pledge_warranty_escrow",
    type: "function",
    inputs: [{ name: "vault_id", type: "u64" }],
    outputs: [],
  },
  {
    name: "file_lemon_claim",
    type: "function",
    inputs: [
      { name: "vault_id", type: "u64" },
      { name: "diagnostic_log_url", type: "string" },
    ],
    outputs: [],
  },
  {
    name: "adjudicate_lemon_claim",
    type: "function",
    inputs: [{ name: "vault_id", type: "u64" }],
    outputs: [],
  },
  {
    name: "appeal_verdict",
    type: "function",
    inputs: [
      { name: "vault_id", type: "u64" },
      { name: "dispute_reason", type: "string" },
    ],
    outputs: [],
  },
  {
    name: "adjudicate_appeal",
    type: "function",
    inputs: [
      { name: "vault_id", type: "u64" },
      { name: "supplemental_log_url", type: "string" },
    ],
    outputs: [],
  },
  {
    name: "finalize_settlement",
    type: "function",
    inputs: [{ name: "vault_id", type: "u64" }],
    outputs: [],
  },
  {
    name: "cancel_or_reclaim",
    type: "function",
    inputs: [{ name: "vault_id", type: "u64" }],
    outputs: [],
  },
  {
    name: "get_vault",
    type: "function",
    inputs: [{ name: "vault_id", type: "u64" }],
    outputs: [{ name: "data", type: "string" }],
  },
  {
    name: "get_all_vaults",
    type: "function",
    inputs: [],
    outputs: [{ name: "data", type: "string" }],
  },
  {
    name: "get_vault_pledges",
    type: "function",
    inputs: [{ name: "vault_id", type: "u64" }],
    outputs: [{ name: "data", type: "string" }],
  },
  {
    name: "get_reputation_profile",
    type: "function",
    inputs: [{ name: "user_address", type: "Address" }],
    outputs: [{ name: "data", type: "string" }],
  },
  {
    name: "get_oem_leaderboard",
    type: "function",
    inputs: [],
    outputs: [{ name: "data", type: "string" }],
  },
  {
    name: "get_stats",
    type: "function",
    inputs: [],
    outputs: [{ name: "data", type: "string" }],
  },
];
