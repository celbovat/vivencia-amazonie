# -*- coding: utf-8 -*-
"""Ikony zastavek trasy. 24x24, jedna cesta, fill=currentColor.
Kazda zastavka ma vlastni ikonu a dohromady vypravuji sestup
z velkomesta do vesnice: mrakodrapy -> nizsi mesto -> mestecko ->
ricni pristav -> kupixawa."""
IKONY = {
    # letadlo pri startu (odlet z Prahy)
    "vzlet": "M2.5 19.5h19V21h-19zM21.9 8.6a1.4 1.4 0 0 0-1.7-1L15.1 9 8.6 3.6 "
             "6.4 4.2l3.9 6.1-4.1 1.1L4.4 10l-1.6.4 1.9 4.2 15.7-4.2a1.4 1.4 0 0 0 "
             "1.5-1.8z",
    # Sao Paulo: hustá řádka věžáků s okny a anténou
    "velkomesto": "M2 21V9.6h6.1V21H2zM9.1 21V4.8h5.6V21H9.1zM11.4 4.8V1.9h1v2.9h-1zM15.7 21V7.4h6.3V21h-6.3zM3.4 11.2h1.6v1.7H3.4zM6.1 11.2h1.6v1.7H6.1zM3.4 14.4h1.6v1.7H3.4zM6.1 14.4h1.6v1.7H6.1zM3.4 17.6h1.6v1.7H3.4zM6.1 17.6h1.6v1.7H6.1zM10.4 6.9h1.4v1.7h-1.4zM12.4 6.9h1.4v1.7h-1.4zM10.4 10.1h1.4v1.7h-1.4zM12.4 10.1h1.4v1.7h-1.4zM10.4 13.3h1.4v1.7h-1.4zM12.4 13.3h1.4v1.7h-1.4zM10.4 16.5h1.4v1.7h-1.4zM12.4 16.5h1.4v1.7h-1.4zM17 9.4h1.7v1.7H17zM19.6 9.4h1.7v1.7h-1.7zM17 12.6h1.7v1.7H17zM19.6 12.6h1.7v1.7h-1.7zM17 15.8h1.7v1.7H17zM19.6 15.8h1.7v1.7h-1.7z",
    # Rio Branco: nižší město, sedlová střecha, vodojem, okna
    "mesto": "M1.4 21v-6.4l3.6-2.9 3.6 2.9V21H1.4zM9.6 21V9.9h6.1V21H9.6zM11.6 9.9V7.6h2.1v2.3h-2.1zM16.6 21v-7.9h6V21h-6zM3.2 15.6h1.4v1.6H3.2zM5.4 15.6h1.4v1.6H5.4zM3.2 18.4h1.4v1.6H3.2zM5.4 18.4h1.4v1.6H5.4zM10.9 11.8h1.5v1.7h-1.5zM13.1 11.8h1.5v1.7h-1.5zM10.9 15h1.5v1.7h-1.5zM13.1 15h1.5v1.7h-1.5zM10.9 18.2h1.5v1.7h-1.5zM13.1 18.2h1.5v1.7h-1.5zM17.9 15h1.4v1.6h-1.4zM20 15h1.4v1.6H20zM17.9 18h1.4v1.6h-1.4zM20 18h1.4v1.6H20z",
    # Tarauaca: mestecko, sedlove strechy
    "mestecko": "M1.6 21v-6.2l4.2-3.4 4.2 3.4V21H1.6zm9.6 0V9.6l5.3-4.2 5.3 4.2V21H11.2z"
                "m3.1-6.8h4.4v-2.6h-4.4v2.6z",
    # Jordao: ricni pristav, domky nad vodou
    "pristav": "M3.4 12.4V8.7l2.9-2.3 2.9 2.3v3.7H3.4zm7.6 0V6.9l3.4-2.7 3.4 2.7v5.5H11z"
               "M1.4 15.9c1.6 0 1.6 1.3 3.2 1.3s1.6-1.3 3.2-1.3 1.6 1.3 3.2 1.3 1.6-1.3 "
               "3.2-1.3 1.6 1.3 3.2 1.3 1.6-1.3 3.2-1.3v1.7c-1.6 0-1.6 1.3-3.2 1.3s-1.6-"
               "1.3-3.2-1.3-1.6 1.3-3.2 1.3-1.6-1.3-3.2-1.3-1.6 1.3-3.2 1.3-1.6-1.3-3.2-"
               "1.3v-1.7z",
    # Chico Curumim: kupixawa, siroka doskova strecha a capka
    "kupixawa": "M12 2.6a1.5 1.5 0 0 1 1.5 1.5c0 .5-.3.9-.7 1.2 3.9 1.7 7.7 5 8.8 8.5H2.4"
                "c1.1-3.5 4.9-6.8 8.8-8.5a1.5 1.5 0 0 1-.7-1.2A1.5 1.5 0 0 1 12 2.6zM4.6 "
                "15.3h14.8V21h-4.6v-3.5h-5.6V21H4.6v-5.7z",
}
