CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shop_name VARCHAR(150) NOT NULL,
    location VARCHAR(150) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    pack_size VARCHAR(30) NOT NULL,
    quantity_kg INT NOT NULL,

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
);