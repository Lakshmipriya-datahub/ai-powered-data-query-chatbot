
CREATE DATABASE real_world_project;
USE real_world_project;


CREATE TABLE orders (
    Order_ID VARCHAR(20) PRIMARY KEY,
    Order_Date DATE,
    Customer_ID VARCHAR(20),
    Gender VARCHAR(10),
    Age INT,
    City VARCHAR(50),
    Category VARCHAR(50),
    Sub_Category VARCHAR(50),
    Product VARCHAR(100),
    Quantity INT,
    Unit_Price DECIMAL(10,2),
    Discount DECIMAL(5,2),
    Payment_Method VARCHAR(30),
    Shipping_Mode VARCHAR(30),
    Rating INT,
    Delivery_Days INT,
    Returned VARCHAR(5),
    Customer_Type VARCHAR(20),
    Sales DECIMAL(10,2),
    Profit DECIMAL(10,2),
    Review TEXT
);

SELECT * FROM orders LIMIT 30;

SELECT COUNT(*) AS Total_Records FROM orders;

# DATA CLEANING........................

# Inconsistent Values

# accidental ga row update cheyakunda prevent cheyadaniki idhi eppudu on lo undhi 
# so manam danni off chesi updates chesaka malli on cheyali

SET SQL_SAFE_UPDATES = 0; 

UPDATE orders
SET Gender = 'Male'
WHERE LOWER(Gender) = 'male';

UPDATE orders
SET Gender = 'Female'
WHERE LOWER(Gender) = 'female';

UPDATE orders
SET Gender = 'Female'
WHERE Gender = 'F';

UPDATE orders
SET Gender = 'Male'
WHERE Gender = 'M';

SELECT Gender
FROM orders;

SET SQL_SAFE_UPDATES = 1; # updating aipoyaka safe mode malli on cheyaliiiii

# Missing Values

SELECT COUNT(*) AS Missing_Values 
FROM orders
WHERE Gender = '';

ALTER TABLE orders MODIFY Gender VARCHAR(20);

UPDATE orders
SET Gender = 'Not Mentioned'
WHERE Gender = '';

SELECT Gender , COUNT(*) AS Gender_Count
FROM orders
GROUP BY Gender;

SELECT COUNT(*) AS Missing_Values 
FROM orders 
WHERE City = ''; 

SELECT City , COUNT(*) AS City_Count
FROM orders
GROUP BY City;

UPDATE orders
SET City = 'Other'
WHERE City = '';

SELECT COUNT(*) AS Missing_values
FROM orders 
WHERE Shipping_Mode = '';

SELECT Shipping_Mode,COUNT(Shipping_Mode)
FROM orders
GROUP BY Shipping_Mode;

UPDATE orders
SET Shipping_Mode = 'Standard'
WHERE Shipping_Mode = ''; # group by chesi edhi ekkuva count unte adhe pettestammm

# Inko Approach - Advanceddddd

SELECT MIN(Delivery_Days), MAX(Delivery_Days), ROUND(AVG(Delivery_Days),0) AS Avg_Delivery_Days
FROM orders
WHERE Delivery_Days IS NOT NULL;

UPDATE orders
SET Shipping_Mode = 
    CASE 
        WHEN Delivery_Days = 1 THEN 'Same Day'
        WHEN Delivery_Days BETWEEN 2 AND 3 THEN 'Express'
        ELSE 'Standard'
    END
WHERE Shipping_Mode = ''; 
# Okavela nulls unte OR use chesi Shipping_Mode IS NULL ani pettocchu

SELECT COUNT(*) AS Missing_Values
FROM orders 
WHERE Review = '';

UPDATE orders
SET Review = 'No Review Given'
WHERE Review = '';

