from django.urls import path
from . import views

urlpatterns = [
    # URLs para Productos
    path('', views.home, name='home'),
    path('productos/', views.lista_productos, name='listar_productos'),
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('producto/actualizar/<int:producto_id>/', views.actualizar_producto, name='actualizar_producto'),

    # URLs para Pedidos
    path('crear/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('detalle/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    
    #path('detalle/<int:pedido_id>/<path:comprobante_url>/', views.detalle_pedido, name='detalle_pedido'),
    path('confirmar/<int:pedido_id>/', views.confirmar_pedido, name='confirmar_pedido'),
    path('eliminar_pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('agregar_producto_al_pedido/<int:pedido_id>/', views.agregar_producto_al_pedido, name='agregar_producto_al_pedido'),
    path('eliminar_item/<int:item_id>/', views.eliminar_item_pedido, name='eliminar_item_pedido'),
    # URLs para el Carrito de Compras
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('actualizar_cantidad_ajax/<int:producto_id>/', views.actualizar_cantidad_ajax, name='actualizar_cantidad_ajax'), # URL para AJAX
    path('actualizar_pedido/<int:pedido_id>/', views.actualizar_pedido, name='actualizar_pedido'),
    # URLs para la autenticación
    path('politica-privacidad/', views.politica_privacidad, name='politica_privacidad'),
    path('terminos-condiciones/', views.terminos_condiciones, name='terminos_condiciones'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    
]