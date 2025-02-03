import { createPublicClient, createWalletClient, http } from 'viem/index.js'
import { baseSepolia } from 'viem/chains/index.js'
import { privateKeyToAccount } from 'viem/accounts/index.js'
import { Agent } from 'agentkit/index.js'
import * as dotenv from 'dotenv'

dotenv.config()

const transport = http(process.env.BASE_SEPOLIA_RPC_URL)

export class NFTService {
  private agent: Agent

  constructor() {
    const account = privateKeyToAccount(`0x${process.env.BACKEND_WALLET_PRIVATE_KEY}`)
    const client = createWalletClient({
      account,
      chain: baseSepolia,
      transport
    })
    this.agent = new Agent({
      client,
      chain: baseSepolia
    })
  }

  async mintNFT(
    recipientAddress: string,
    metadata: {
      name: string
      description: string
      image_url: string
      attributes: string
    }
  ): Promise<{ tokenId: bigint; transactionHash: string }> {
    try {
      // Convert attributes string to object
      const attributes = JSON.parse(metadata.attributes)

      // Create NFT metadata
      const tokenMetadata = {
        name: metadata.name,
        description: metadata.description,
        image: metadata.image_url,
        attributes
      }

      // Mint NFT using agentkit
      const result = await this.agent.mintNFT({
        to: recipientAddress,
        metadata: tokenMetadata,
        contractAddress: process.env.NFT_CONTRACT_ADDRESS as `0x${string}`
      })

      return {
        tokenId: result.tokenId,
        transactionHash: result.transactionHash
      }
    } catch (error) {
      console.error('Error minting NFT:', error)
      throw error
    }
  }

  async getTokenURI(tokenId: bigint): Promise<string> {
    try {
      const uri = await this.agent.getTokenURI({
        tokenId,
        contractAddress: process.env.NFT_CONTRACT_ADDRESS as `0x${string}`
      })
      return uri
    } catch (error) {
      console.error('Error getting token URI:', error)
      throw error
    }
  }
}
