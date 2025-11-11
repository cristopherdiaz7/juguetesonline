from rest_framework.test import APIClient
from ventas.models import Pedido, PedidoItem, Producto

def main():
    client = APIClient()
    resp = client.post('/api/token/', {'username':'cristodiaz','password':'43892221'}, format='json')
    print('token status', resp.status_code)
    access = resp.data.get('access') if resp.status_code == 200 else None
    print('access present:', bool(access))

    p = Pedido.objects.filter(estado='pendiente').first()
    if not p:
        print('No pending pedido found.')
        return

    items = list(PedidoItem.objects.filter(pedido=p).select_related('producto'))
    print('Pedido id', p.id)
    print('Before stocks:')
    for it in items:
        prod = it.producto
        print(f'  {prod.nombre}: {prod.stock} (needed {it.cantidad})')

    client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
    pr = client.patch(f'/api/pedidos/{p.id}/', {'estado':'aprobado'}, format='json')
    print('patch status', pr.status_code)
    print('response data:', getattr(pr, 'data', None))

    print('After stocks:')
    for it in items:
        prod = Producto.objects.get(id=it.producto.id)
        print(f'  {prod.nombre}: {prod.stock}')

if __name__ == '__main__':
    main()
