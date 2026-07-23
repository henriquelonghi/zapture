export interface ProductOut {
  id: string
  sku: string | null
  name: string
  category: string | null
  unit_cost: number | null
}

export interface ProductCostIn {
  unit_cost: number
}
