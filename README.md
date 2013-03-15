mvcafe
======

A minimum viable cafe app.

APIs

    POST /login

Post data is like: 
    {
      userId: "asdfsadf",
      name: "Asfd ASdf",
      photo: "http://twitter.com/asdfwd/photo"
    }

Respond with 
    { status: true } 
or 
    { status: false, message: "Go away, we don't like you." }


    POST /orders

Example post data:

    { 
      "type": "cappuccino"
    }

respond with 
    { status: true } 
or 
    { status: false, message: "Cafe is closed" }

    POST /orders/<orderId>/start

No postdata; respond with { status: true } or { status: false, message: "Can't find that order" }

    POST /orders/<orderId>/ready

No postdata; respond with { status: true } or { status: false, message: "You're not Sharon" }

    POST /orders/<orderId>/cancel
    
No postdata; respond with { status: true } or { status: false, message: "That's not your order." }


    GET /status

Respond with:

    {
      time: "234897239487",
      orders: [
        {
          id: "98238749",
          type: "cappuccino",
          userId: "2347987",
          orderedAt: "1029837938457",
          startedAt: "2348793847593",
          readyAt: "98345729384"
        }
      ],
      users: [
        {
          id: "asdfsadf",
          name: "Asdf Asdf",
          photo: "http://"
        }
      ]
    }
