import { createWalletClient, http } from 'viem'
import { baseSepolia } from 'viem/chains'
import { privateKeyToAccount } from 'viem/accounts'
import { Agent } from 'agentkit'
import * as dotenv from 'dotenv'
import * as fs from 'fs'
import * as path from 'path'

dotenv.config()

export class NFTDeployService {
  private agent: Agent

  constructor() {
    const account = privateKeyToAccount(`0x${process.env.BACKEND_WALLET_PRIVATE_KEY}`)
    const client = createWalletClient({
      account,
      chain: baseSepolia,
      transport: http(process.env.BASE_SEPOLIA_RPC_URL)
    })
    this.agent = new Agent({
      client,
      chain: baseSepolia
    })
  }

  async deployNFTContract(name: string, symbol: string): Promise<{ 
    contractAddress: string
    transactionHash: string 
  }> {
    try {
      // Deploy NFT contract using agentkit
      const result = await this.agent.deployNFTContract({
        name,
        symbol,
        baseTokenURI: '', // Will be set per-token during minting
      })

      // Update .env file with contract address
      const envPath = path.join(process.cwd(), '.env')
      let envContent = fs.readFileSync(envPath, 'utf8')

      // Remove old NFT contract address if exists
      envContent = envContent.replace(/\nNFT_CONTRACT_ADDRESS=.*/, '')

      // Add new contract address
      envContent += `\n# NFT Configuration\nNFT_CONTRACT_ADDRESS='${result.contractAddress}'`

      // Write back to .env
      fs.writeFileSync(envPath, envContent.trim() + '\n')

      return {
        contractAddress: result.contractAddress,
        transactionHash: result.transactionHash
      }
    } catch (error) {
      console.error('Error deploying NFT contract:', error)
      throw error
    }
  }

  async verifyDeployment(contractAddress: string): Promise<boolean> {
    try {
      // Verify contract exists and is accessible
      const code = await this.agent.client.getBytecode({ address: contractAddress })
      return code !== undefined && code !== '0x'
    } catch (error) {
      console.error('Error verifying NFT contract:', error)
      return false
    }
  }
}
