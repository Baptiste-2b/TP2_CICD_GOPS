-- NULL means the producer has not declared a stock limit.
ALTER TABLE products ADD COLUMN IF NOT EXISTS stock INTEGER CHECK (stock >= 0);
