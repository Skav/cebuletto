create table shops(
	idShop int auto_increment primary key,
	shopName varchar(45) not null,
	searchCounter int unsigned not null default 0);

create table productsTags(
    idProductTags int auto_increment primary key,
	productTags varchar(45) not null,
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
	idTagsToProduct int auto_increment primary key,
	idProduct int not null references products(idProduct),
    idProductTags int not null references productsTags(idProductTags),
    lastUpdate timestamp not null default now() on update now());
