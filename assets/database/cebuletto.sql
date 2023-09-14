create table shops(
	idShop int auto_increment primary key,
	name varchar(45) not null,
	searchCounter int unsigned not null default 0);

create table productsTags(
    idProductTag int auto_increment primary key,
	tag varchar(45) not null,
	searchCounter int unsigned not null default 1);

create table products(
	idProduct int auto_increment primary key,
	idShop int not null references shops(idShop),
	name varchar(100) not null,
	price float(6,2) not null default 0,
	discountPrice float(6,2) not null default 0,
	productUrl varchar(200) not null,
	imageUrl varchar(200),
	available boolean not null default true,
	lastUpdate timestamp not null default now() on update now());

create table tagsToProducts(
	idTagToProduct int auto_increment primary key,
	idProduct int not null references products(idProduct),
    idProductTag int not null references productsTags(idProductTag),
    lastUpdate timestamp not null default now() on update now());

create table historyOfPrices(
    idHistoryOfPrice int auto_increment primary key,
    idProduct int not null references products(idProduct),
    price float(6,2) not null default 0,
    discountPrice float(6,2) not null default 0,
    priceDate timestamp not null default now() on update now());
