const url = 'http://127.0.0.1:5000/';

window.onload = async () =>
{
    await createCheckbox();
    document.getElementById('add').addEventListener("click", addProduct, false);
    document.getElementById('del').addEventListener("click", delProduct, false);
}

async function getData(endpoint, options=null)
{
    const response = await fetch(url+endpoint, options)
    const data = await response.json()

    if(response.status == 500)
    {
        throw {
            name: "InternalServerError",
            message: "Internal server error",
            toString:function(){return this.name+": "+this.message}
        }
    }
    else if(response.status == 404)
    {
        throw {
            name: "PageNotFound",
            message: "Page not found",
            toString:function(){return this.name+": "+this.message}
        }
    }
    else if(response.status == 400)
    {
        throw {
            name: "BadRequestError",
            message: data,
            toString:function(){return this.name+": "+this.message}
        }
    }

    return data
}

async function createCheckbox()
{
    try
    {
        let items = await getData("shops");

        let shopsDiv = document.createElement('div');
        let searchForm = document.getElementById('searchForm');
        shopsDiv.id = "shops";

        for(i=0; i<Object.keys(items).length;i++)
        {
            let checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = items[i];
            checkbox.id = items[i];
            checkbox.name = 'shop';
            checkbox.checked = true;
            checkbox.className = 'checkbox_shop';
            let label = document.createElement('label');
            label.setAttribute("for",checkbox.id);
            label.innerHTML = items[i];
            let item = document.createElement('div');
            item.className = "item_shop";

            item.appendChild(checkbox);
            item.appendChild(label);
            shopsDiv.appendChild(item);
        }
        searchForm.insertBefore(shopsDiv, searchForm.firstChild);
    }
    catch(error)
    {
        if(error instanceof TypeError && error.toString().includes('NetworkError'))
        {
            console.log(error);
            createErrorDiv("Bład połaczenia z serwerem, spróbuj pózniej");
        }
        else if(error.name == "InternalServerError")
            createErrorDiv("Bład serwera, prosze spróbować pózniej");
        else if(error.name == "PageNotFoundError")
        {
            console.log(error)
            createErrorDiv("Nie można znaleść strony");
        }
    }
}

function addProduct()
{
    let input = document.createElement('input');
    input.name = "product_name";
    input.className = "products_item";
    input.type = 'text';
    input.placeholder = "Wpisz nazwe produktu";
    input.required = true;
    let div = document.getElementById('products');
    div.appendChild(input);
}

function delProduct()
{
    let div = document.getElementById("products");
    let inputs = document.getElementsByName("product_name");
    if(inputs.length > 1)
        div.lastChild.remove();
}

async function getValues()
{
    try
    {
        startLoadingScreen();
        clearError();
        removeHighlightFromProductsFields();
        let checkedShops = getCheckedShops();
        let products_list = getUserProducts();

        let json = {
            "products_list": products_list,
            "shops_list": checkedShops
        }

        const options = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(json)
        }


        const data = await getData('find', options)
        let {final, byProduct} = findCheapest(data);
        drawProducts(data, final, byProduct);
        stopLoadingScreen();
    }
    catch(error)
    {
        stopLoadingScreen();
        if(error.name == "NotShopsSelected")
            createErrorDiv("Musisz wbrac sklepy!");
        else if(error.name == "NotProductsSelected")
            createErrorDiv("Musisz podać produkty!");
        else if(error.name == "InternalServerError")
            createErrorDiv("Bład serwera, prosze spróbować pózniej");
        else if(error.name == "PageNotFoundError")
        {
            console.log(error)
            createErrorDiv("Nie można znaleść strony");
        }
        else if(error.name == "BadRequestError")
        {
            console.log(error.message)
            createErrorDiv("Wprowadzone dane są błedne")
        }
        else
            console.log(error)
    }
}

function getCheckedShops()
{
    let shops = document.getElementsByName("shop");
    let checkedShops = [];
    for(i=0; i<shops.length; i++)
    {
        if(shops[i].checked)
            checkedShops.push(shops[i].value);
    }

    if(checkedShops.length == 0)
        throw {
            name: "NotShopsSelected",
            message: "Empty checkbox shop list",
            toString: function(){return this.name + ": " + this.message}
        };

    return checkedShops;
}

function getUserProducts()
{
    let products = document.getElementsByName("product_name");
    let products_list = [];
    let error = false;

    Array.from(products).forEach((product) =>
    {
        if(product.value)
            products_list.push(product.value);
        else
        {
            product.classList.add('empty')
            error = true;
        }
    })

    if(error)
        throw {
            name: "NotProductsSelected",
            message: "The products list is empty",
            toString: function(){return this.name+": "+this.message}
        }

    return products_list;
}

function findCheapest(jsonData)
{
    let {cheapest, final} = findCheapestInShop(jsonData);
    let byProduct = findCheapestByProduct(cheapest, jsonData);
    return {final, byProduct};
}

function findCheapestInShop(jsonData)
{
    let cheapest = {};
    let final = {};
    for(product in jsonData)
    {
        cheapest[product] = {};
        final[product] = {};
        for(shop in jsonData[product])
        {
            cheapest[product][shop] = {};
            final[product][shop] = {};
            final_price = Number.MAX_VALUE;
            for(item in jsonData[product][shop])
            {
                if(jsonData[product][shop][item] == "Brak")
                {
                    cheapest[product][shop] = {};
                    final[product][shop] = {};
                    cheapest[product][shop][item] = "Brak";
                    final[product][shop][item] = "Brak";
                }
                else
                {
                    let price = parseFloat(jsonData[product][shop][item]["price"]);
                    let discount_price = parseFloat(jsonData[product][shop][item]["discount_price"]);

                    if(price < final_price && discount_price < final_price || final_price == 0)
                    {
                        if (discount_price > 0 && discount_price < price)
                            final_price = discount_price;
                        else
                            final_price = price;

                        if(isEmpty(cheapest[product][shop]))
                        {
                            cheapest[product][shop][item] = {"price": final_price};
                            final[product][shop][item] = jsonData[product][shop][item];
                        }
                        else if(!isLower(cheapest[product][shop], final_price))
                        {
                            cheapest[product][shop] = {};
                            final[product][shop] = {};
                            cheapest[product][shop][item] = {"price": final_price};
                            final[product][shop][item] = jsonData[product][shop][item];
                        }
                    }
                }
            }
        }
    }
    return {cheapest, final}
}


function findCheapestByProduct(data, jsonData)
{
    let cheapest_value = Number.MAX_VALUE;
    let cheapest_product = {};

    for(product in data)
    {
        cheapest_product[product] = {};
        for(shop in data[product])
        {
            cheapest_product[product][shop] = {};
            if(!isEmpty(data[product][shop]))
            {
                let item = Object.keys(data[product][shop]);
                if(isLower(data[product][shop], cheapest_value))
                {
                    cheapest_product[product] = {};
                    cheapest_product[product][shop] = {};
                    cheapest_product[product][shop][item] = jsonData[product][shop][item];
                }
                else if (data[product][shop][item] == "Brak")
                {
                    cheapest_product[product] = {};
                    cheapest_product[product][shop] = {};
                    cheapest_product[product][shop][item] = "Brak";
                }
            }
        }
    }

    return cheapest_product;
}

function drawProducts(allProductsList, cheapestInShop, cheapestByProduct)
{
    let results = document.getElementById('results');
    clearContainer(results);

    let {byProduct, inShop, allProducts} = createResultsElements();

    let elements = Array(byProduct, inShop, allProducts);
    let datas = Array(cheapestByProduct, cheapestInShop, allProductsList);

    for(i=0; i<elements.length; i++)
    {
        for(item in datas[i])
        {
            let itemName = document.createElement('div');
            itemName.className = "item";
            itemName.innerHTML = item;

            for(shop in datas[i][item])
            {
                let shopName = document.createElement('div');
                let productContainer = document.createElement('div');
                productContainer.className = "product_container";
                shopName.className = "shop";
                shopName.innerHTML = shop;

                for(product in datas[i][item][shop])
                {
                    let singleProduct = document.createElement('div');
                    singleProduct.className = "product";

                    if(datas[i][item][shop][product] == "Brak")
                    {
                        singleProduct.classList.add("empty");
                        var productName = createProductName();
                        var price = '';
                    }
                    else
                    {
                        let url = datas[i][item][shop][product]["link"];
                        singleProduct.setAttribute('data-url', url);
                        var productName = createProductName(product);

                        let discount_price = datas[i][item][shop][product]["discount_price"];
                        let regular_price = datas[i][item][shop][product]["price"];

                        var price = createPrice(regular_price, discount_price);
                    }
                    productContainer.appendChild(connectProductElements(singleProduct, productName, price));
                    shopName.appendChild(productContainer);
                    itemName.appendChild(shopName);
                    elements[i].appendChild(itemName);
                }
            }
        }
        results.appendChild(elements[i])
    }
    addActionLisnerForProducts();
}


function clearContainer(container)
{
    container.innerHTML = '';
}

function createResultsElements()
{
    let byProduct = document.createElement('div');
    let inShop = document.createElement('div');
    let allProducts = document.createElement('div');

    byProduct.id = "cheapestByProduct";
    byProduct.className = "products_list";
    byProduct.innerHTML = "Najtańsze produkty";
    inShop.id = "cheapestInShop";
    inShop.className = "products_list";
    inShop.innerHTML = "Najtańsze produkty w danym sklepie";
    allProducts.id = "allProducts";
    allProducts.className = "products_list";
    allProducts.innerHTML = "Wszystkie produkty";

    return {byProduct, inShop, allProducts};
}

function createProductName(product)
{
    let productName = document.createElement('div');
    productName.className = "product_name";

    if (!product)
    {
        productName.innerHTML = "Brak danego produktu w sklepie";
        productName.classList.add("empty");
    }
    else
        productName.innerHTML = product;
    return productName;
}

function createPrice(regular_price, discount_price)
{
    let price = document.createElement('div');
    let regular = document.createElement('span');
    price.className = "price";
    regular.className = "price";
    regular.innerHTML = `${regular_price} zł`;

    if(discount_price > 0)
    {
        let discount = document.createElement('span');
        discount.className = "price";
        regular.classList.add("base");
        discount.innerHTML = `${discount_price} zł `;

        price.appendChild(discount);
    }
    price.appendChild(regular);
    return price;
}

function connectProductElements(singleProduct, productName, price)
{
    singleProduct.appendChild(productName);
    if(price) singleProduct.appendChild(price);
    return singleProduct;
}

function addActionLisnerForProducts()
{
    let products = document.getElementsByClassName("product");

    Array.from(products).forEach((product) =>
    {
        if(product.getAttribute("data-url"))
        {
            product.addEventListener("click", function()
            {
                window.open(this.getAttribute("data-url"), '_blank');
            });
        }
    }, false);
}


function isEmpty(obj){
    return Object.keys(obj).length === 0;
}

function isLower(obj, value)
{
    let key = Object.keys(obj);
    return obj[key]["price"] < value;
}

function createErrorDiv(message)
{
    let errorDiv = document.createElement('div');
    let searchSection = document.getElementById('search');
    errorDiv.id = "error";
    errorDiv.innerHTML = message;
    if(document.getElementById('shops'))
        searchSection.insertBefore(errorDiv, searchSection.lastChild);
    else searchSection.insertBefore(errorDiv, searchSection.firstChild);
}

function clearError()
{
    let error = document.getElementById('error');

    if(error)
        error.remove();
}


function startLoadingScreen()
{
    let loading = document.createElement("div");
    loading.id = "loading";
    loading.innerHTML = "Ładowanie zawarości, moze to potrwac kilka minut...";
    document.body.insertBefore(loading, document.body.firstChild);
}

function stopLoadingScreen()
{
    document.body.firstChild.remove();
}

function removeHighlightFromProductsFields()
{
    let products = document.getElementsByName('product_name');

    Array.from(products).forEach((product) =>
    {
        product.classList.remove('empty');
    });
}