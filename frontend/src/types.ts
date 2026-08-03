/* Tipos compartidos del sistema Consumo Estratégico */

export interface User {
  id: number
  name: string
  email: string
  created_at: string
}

export interface UserSummary extends User {
  total_purchases: number
  total_spent: number
}

export interface UserDetail extends UserSummary {
  avg_per_purchase: number
  favorite_product: string | null
  most_used_payment: string | null
  last_purchase_date: string | null
}

export type PaymentMethod = 'Efectivo' | 'Tarjeta' | 'Transferencia'

export interface Purchase {
  id: number
  user_id: number
  user_name: string
  product: string
  quantity: number
  price: number
  total: number
  purchase_date: string
  purchase_time: string
  payment_method: PaymentMethod
  created_at: string
}

export interface PurchaseCreate {
  user_id: number
  product: string
  quantity: number
  price: number
  purchase_date: string
  purchase_time: string
  payment_method: PaymentMethod
}

export interface ImportValidation {
  valid_rows: number
  error_rows: number
  errors: Array<{ row: number; errors: string[] }>
}

export interface ImportResponse {
  import_id: number
  status: string
  filename: string
  rows_detected: number
  preview: Record<string, string>[]
  validation: ImportValidation
}

export interface TokenData {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface TopProduct {
  product: string
  count: number
  total_spent: number
}

export interface PredictedPurchase {
  product: string
  predicted_quantity: number
  predicted_price: number
  predicted_total: number
  predicted_date: string
  frequency_days: number
  confidence: number
  purchase_count: number
  total_spent: number
}

export interface RawPredictedPurchase {
  product: string
  predicted_quantity: number | string
  predicted_price: number | string
  predicted_total: number | string
  predicted_date: string
  frequency_days: number | string
  confidence: number | string
  purchase_count: number | string
  total_spent: number | string
}

export interface AnalysisSummary {
  user_id: number
  user_name: string
  period: {
    from: string
    to: string
  }
  summary: {
    total_purchases: number
    total_spent: number
    average_per_purchase: number
    favorite_product: string | null
    most_used_payment_method: string | null
  }
  top_products: TopProduct[]
  payment_methods: Record<string, number>
  predictions: PredictedPurchase[]
}
