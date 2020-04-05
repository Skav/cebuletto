const url = 'http://127.0.0.1:5000/'

async function getData()
{
    const response = await fetch(url+"shops");
    const shops = await response.json()
    console.log(shops)
    return shops
}

async function createCheckbox()
{
    let items = await getData()

    let div = document.getElementById('shops')
    for(i=0; i<Object.keys(items).length;i++)
    {
        let checkbox = document.createElement('input');
        checkbox.type = 'checkbox'
        checkbox.value = items[i]
        checkbox.id = items[i]
        checkbox.name = 'shop'
        checkbox.checked = true
        checkbox.className = 'checkbox_shop'
        let label = document.createElement('label')
        label.setAttribute("for",checkbox.id)
        label.innerHTML = items[i]
        let item = document.createElement('div')
        item.className = "item_shop"

        item.appendChild(checkbox)
        item.appendChild(label)
        div.appendChild(item)
    }
}

function addProduct()
{
    let input = document.createElement('input')
    input.name = "product_name"
    input.type = 'text'
    input.placeholder = "Wpisz nazwe produktu"
    input.required = true;
    let div = document.getElementById('products')
    div.appendChild(input)
}

function delProduct()
{
    let div = document.getElementById("products")
    let inputs = document.getElementsByName("product_name")
    if(inputs.length > 1)
        div.lastChild.remove()
}

function startLoading()
{
    let loading = document.createElement("div")
    loading.id = "loading"
    loading.innerHTML = "Ładowanie zawarości, moze to potrwac kilka minut..."
    document.body.insertBefore(loading, document.body.firstChild)
}

function stopLoading()
{
    document.body.firstChild.remove()
}

function getCheckedShops()
{
    let shops = document.getElementsByName("shop")
    let checkedShops = []
    for(i=0; i<shops.length; i++)
    {
        if(shops[i].checked)
            checkedShops.push(shops[i].value)
    }
    return checkedShops
}

function getUserProducts()
{
    let products = document.getElementsByName("product_name")
    let products_list = []

    for(let i=0; i<products.length; i++)
        products_list.push(products[i].value)

    return products_list
}

async function get_values()
{
    startLoading()
    let checkedShops = getCheckedShops()
    let products_list = getUserProducts()

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


    const response = await fetch(url+'find', options)
    const data = await response.json()
    let {final, byProduct} = findCheapest(data)
    drawProducts(data, final, byProduct)
    stopLoading()
}

function findCheapest(jsonData)
{
    let {cheapest, final} = findCheapestInShop(jsonData)
    let byProduct = findCheapestByProduct(cheapest, jsonData)
    return {final, byProduct}
}

function findCheapestInShop(jsonData)
{
    let cheapest = {}
    let final = {}
    for(product in jsonData)
    {
        cheapest[product] = {}
        final[product] = {}
        for(shop in jsonData[product])
        {
            cheapest[product][shop] = {}
            final[product][shop] = {}
            final_price = Number.MAX_VALUE
            for(item in jsonData[product][shop])
            {
                if(jsonData[product][shop][item] == "Brak")
                {
                    cheapest[product][shop] = {}
                    final[product][shop] = {}
                    cheapest[product][shop][item] = "Brak"
                    final[product][shop][item] = "Brak"
                }
                else
                {
                    let price = parseFloat(jsonData[product][shop][item]["price"])
                    let discount_price = parseFloat(jsonData[product][shop][item]["discount_price"])

                    if(price < final_price && discount_price < final_price || final_price == 0)
                    {
                        if (discount_price > 0 && discount_price < price)
                            final_price = discount_price
                        else
                            final_price = price

                        if(isEmpty(cheapest[product][shop]))
                        {
                            cheapest[product][shop][item] = {"price": final_price}
                            final[product][shop][item] = jsonData[product][shop][item]
                        }
                        else if(!isLower(cheapest[product][shop], final_price))
                        {
                            cheapest[product][shop] = {}
                            final[product][shop] = {}
                            cheapest[product][shop][item] = {"price": final_price}
                            final[product][shop][item] = jsonData[product][shop][item]
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
    let cheapest_value = Number.MAX_VALUE
    let cheapest_product = {}

    for(product in data)
    {
        cheapest_product[product] = {}
        for(shop in data[product])
        {
            cheapest_product[product][shop] = {}
            if(!isEmpty(data[product][shop]))
            {
                let item = Object.keys(data[product][shop])
                if(isLower(data[product][shop], cheapest_value))
                {
                    cheapest_product[product] = {}
                    cheapest_product[product][shop] = {}
                    cheapest_product[product][shop][item] = jsonData[product][shop][item]
                }
                else if (data[product][shop][item] == "Brak")
                {
                    cheapest_product[product] = {}
                    cheapest_product[product][shop] = {}
                    cheapest_product[product][shop][item] = "Brak"
                }
            }
        }
    }

    return cheapest_product
}

function isEmpty(obj){
    return Object.keys(obj).length === 0;
}

function isLower(obj, value)
{
    let key = Object.keys(obj)
    return obj[key]["price"] < value
}

function drawProducts(allProductsList, cheapestInShop, cheapestByProduct)
{
    let results = document.getElementById('results')
    clearContainer(results)

    let {byProduct, inShop, allProducts} = createResultsElements()

    let elements = Array(byProduct, inShop, allProducts)
    let datas = Array(cheapestByProduct, cheapestInShop, allProductsList)

    for(i=0; i<elements.length; i++)
    {
        for(item in datas[i])
        {
            let itemName = document.createElement('div')
            itemName.className = "item"
            itemName.innerHTML = item

            for(shop in datas[i][item])
            {
                let shopName = document.createElement('div')
                let productContainer = document.createElement('div')
                productContainer.className = "product_container"
                shopName.className = "shop"
                shopName.innerHTML = shop

                for(product in datas[i][item][shop])
                {
                    let singleProduct = document.createElement('div')
                    singleProduct.className = "product"

                    if(datas[i][item][shop][product] == "Brak")
                    {
                        var productName = createProductName("brak")
                        var price = ''
                    }
                    else
                    {
                        let url = datas[i][item][shop][product]["link"]
                        var productName = createProductName(product, url)

                        let discount_price = datas[i][item][shop][product]["discount_price"]
                        let regular_price = datas[i][item][shop][product]["price"]

                        var price = createPrice(regular_price, discount_price)
                    }
                    productContainer.appendChild(connectProductElements(singleProduct, productName, price))
                    shopName.appendChild(productContainer)
                    itemName.appendChild(shopName)
                    elements[i].appendChild(itemName)
                }
            }
        }
        results.appendChild(elements[i])
    }
}

function connectProductElements(singleProduct, productName, price)
{
    singleProduct.appendChild(productName)
    if(price) singleProduct.appendChild(price)
    return singleProduct
}

function createPrice(regular_price, discount_price)
{
    let price = document.createElement('div')
    let regular = document.createElement('span')
    price.className = "price"
    regular.className = "price"
    regular.innerHTML = `${regular_price} zł`

    if(discount_price > 0)
    {
        let discount = document.createElement('span')
        discount.className = "price"
        regular.classList.add("base")
        discount.innerHTML = `${discount_price} zł `

        price.appendChild(discount)
    }
    price.appendChild(regular)
    return price
}

function createProductName(product, url = '')
{
    let productName = document.createElement('div')
    productName.className = "product_name"

    if(url)
    {
        productLink = createProductLink(url, product)
        productName.appendChild(productLink)
    }
    else if (product == "brak")
    {
        productName.innerHTML = "Brak danego produktu w sklepie"
        productName.classList.add("empty")
    }
    else
        productName.innerHTML = product
    return productName
}

function createProductLink(url, product)
{
    let productLink = document.createElement('a')
    productLink.href = url
    productLink.innerHTML = product
    productLink.setAttribute('target', '_blank')

    return productLink
}

function clearContainer(container)
{
    container.innerHTML = ''
}

function createResultsElements()
{
    let byProduct = document.createElement('div')
    let inShop = document.createElement('div')
    let allProducts = document.createElement('div')

    byProduct.id = "cheapestByProduct"
    byProduct.className = "products_list"
    byProduct.innerHTML = "Najtańsze produkty"
    inShop.id = "cheapestInShop"
    inShop.className = "products_list"
    inShop.innerHTML = "Najtańsze produkty w danym sklepie"
    allProducts.id = "allProducts"
    allProducts.className = "products_list"
    allProducts.innerHTML = "Wszystkie produkty"

    return {byProduct, inShop, allProducts}
}
