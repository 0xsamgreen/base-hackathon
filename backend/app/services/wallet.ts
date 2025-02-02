import { createWalletClient, http, parseEther, WalletClient, type Hash } from 'viem'
import { privateKeyToAccount } from 'viem/accounts'
import { baseSepolia } from 'viem/chains'
import * as crypto from 'crypto'

export class WalletService {
  async createWallet(): Promise<{ address: string; privateKey: string }> {
    // Generate random private key
    const privateKey = crypto.randomBytes(32).toString('hex')
    const account = privateKeyToAccount(`0x${privateKey}`)
    
    // Create wallet client to verify it works
    const client = createWalletClient({
      account,
      chain: baseSepolia,
      transport: http()
    })

    // Get address to verify wallet works
    const address = account.address

    return {
      address,
      privateKey
    }
  }

  async getWalletClient(privateKey: string): Promise<WalletClient> {
    // Create account from private key
    const account = privateKeyToAccount(`0x${privateKey}`)
    
    // Create and return wallet client
    return createWalletClient({
      account,
      chain: baseSepolia,
      transport: http()
    })
  }

  async sendTransaction(privateKey: string, to: string, amount: string): Promise<Hash> {
    const account = privateKeyToAccount(`0x${privateKey}`)
    const client = await this.getWalletClient(privateKey)
    const hash = await client.sendTransaction({
      account,
      chain: baseSepolia,
      to: to as `0x${string}`,
      value: parseEther(amount),
      kzg: undefined // Required by viem v2 but not needed for Base
    })
    return hash
  }
}
