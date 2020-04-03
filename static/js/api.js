const url = 'http://127.0.0.1:5000/'

function hideElement(id)
{
    let elementToHide = document.getElementById(id+"Data")
    if (elementToHide.style.display == 'none')
        elementToHide.style.display = 'flex'
    else
    elementToHide.style.display = 'none'
}

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

async function get_values()
{
    let products = document.getElementsByName("product_name")
    let shops = document.getElementsByName("shop")
    let checkedShops = []
    let products_list = []

    for(i=0; i<shops.length; i++)
    {
        if(shops[i].checked)
            checkedShops.push(shops[i])
    }

    for(let i=0; i<products.length; i++)
        products_list.push(products[i].value)

    let json = {
        "products_list": products_list
    }


    console.log(json)

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(json)
    }

    const response = await fetch(url+'find', options)
    const data = await response.json()
    console.log(data)
    let {final, byProduct} = findCheapest(data)
    drawProducts(data, final, byProduct)
}

function findCheapest(jsonData)
{
    let {cheapest, final} = findCheapestInShop(jsonData)
    let byProduct = findCheapestByProduct(cheapest, jsonData)

    console.log(byProduct)
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
                if(isLower(data[product][shop], cheapest_value))
                {
                    item = Object.keys(data[product][shop])
                    cheapest_product[product] = {}
                    cheapest_product[product][shop] = {}
                    cheapest_product[product][shop][item] = jsonData[product][shop][item]
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
    let byProduct = document.getElementById('cheapestByProduct')
    let InShop = document.getElementById('cheapestInShop')
    let allProducts = document.getElementById('allProducts')

    let elements = Array(byProduct, InShop, allProducts)
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
                let product_container = document.createElement('div')
                product_container.className = "product_container"
                shopName.className = "shop"
                shopName.innerHTML = shop

                for(product in datas[i][item][shop])
                {
                    let productName = document.createElement('div')
                    let productLink = document.createElement('a')
                    let price = document.createElement('div')
                    let discount_price = document.createElement('div')
                    let single_product = document.createElement('div')

                    single_product.className = "product"
                    productName.className = "product_name"
                    price.className = "price"
                    discount_price.className = "discount"

                    if(datas[i][item][shop] == "Brak")
                    {
                        productName.innerHTML = "Brak"
                        price.innerHTML = '0 zł'
                        discount_price.innerHTML = '0 zł'

                        single_product.appendChild(productName)
                        single_product.appendChild(price)
                        single_product.appendChild(discount_price)
                        product_container.appendChild(single_product)
                        shopName.appendChild(product_container)
                        itemName.appendChild(shopName)
                        elements[i].appendChild(itemName)
                        break
                    }

                    productLink.href = datas[i][item][shop][product]["link"]
                    productLink.innerHTML = product
                    productLink.setAttribute('target', '_blank')
                    productName.appendChild(productLink)

                    price.innerHTML = "Cena: " +datas[i][item][shop][product]["price"] + " zł"

                    let discount = datas[i][item][shop][product]["discount_price"]
                    if(datas[i][item][shop][product]["discount_price"] > 0)
                        discount_price.innerHTML = "Zniżka: " + discount + " zł"
                    else
                    discount_price.innerHTML = "Zniżka: Brak"

                    single_product.appendChild(productName)
                    single_product.appendChild(price)
                    single_product.appendChild(discount_price)
                    product_container.appendChild(single_product)
                    shopName.appendChild(product_container)
                    itemName.appendChild(shopName)
                    elements[i].appendChild(itemName)
                }
            }
        }
        elements[i].style.display = 'grid'
    }
}

