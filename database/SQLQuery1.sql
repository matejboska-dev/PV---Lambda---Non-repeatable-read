use boska

-- vytvoøení tabulek
create table categories (
    categoryid int primary key identity(1,1),
    name varchar(50) not null,
    description varchar(200),
    isactive bit default 1
);

create table products (
    productid int primary key identity(1,1),
    categoryid int foreign key references categories(categoryid),
    name varchar(100) not null,
    description varchar(500),
    price float not null,
    stockquantity int not null,
    lastupdated datetime default getdate(),
    status varchar(20) check (status in ('available', 'discontinued', 'out_of_stock'))  -- enum pomocí check constraint
);

create table customers (
    customerid int primary key identity(1,1),
    firstname varchar(50) not null,
    lastname varchar(50) not null,
    email varchar(100) unique not null,
    phonenumber varchar(20),
    registrationdate datetime default getdate()
);

create table orders (
    orderid int primary key identity(1,1),
    customerid int foreign key references customers(customerid),
    orderdate datetime default getdate(),
    totalamount float not null,
    status varchar(20) check (status in ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    isdeleted bit default 0
);

create table orderitems (
    orderid int foreign key references orders(orderid),
    productid int foreign key references products(productid),
    quantity int not null,
    unitprice float not null,
    primary key (orderid, productid)
);

go
-- vytvoøení pohledù
create view vw_productinventory as
select 
    p.productid,
    p.name as productname,
    c.name as categoryname,
    p.price,
    p.stockquantity,
    p.status,
    p.lastupdated
from products p
join categories c on p.categoryid = c.categoryid;
go

go
create view vw_ordersummary as
select 
    o.orderid,
    c.firstname + ' ' + c.lastname as customername,
    o.orderdate,
    o.totalamount,
    count(oi.productid) as totalitems,
    o.status
from orders o
join customers c on o.customerid = c.customerid
join orderitems oi on o.orderid = oi.orderid
group by o.orderid, c.firstname, c.lastname, o.orderdate, o.totalamount, o.status;
go

-- vložení základních dat
insert into categories (name, description) values
('laptopy', 'pøenosné poèítaèe'),
('smartphony', 'mobilní telefony'),
('pøíslušenství', 'doplòky k elektronice');

insert into products (categoryid, name, price, stockquantity, status) values
(1, 'lenovo thinkpad', 25999.99, 10, 'available'),
(2, 'iphone 13', 19999.99, 15, 'available'),
(3, 'usb-c kabel', 299.99, 100, 'available');

insert into customers (firstname, lastname, email, phonenumber) values
('jan', 'novák', 'jan.novak@email.cz', '123456789'),
('marie', 'svobodová', 'marie.s@email.cz', '987654321');