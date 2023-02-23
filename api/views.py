from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import Books,Carts,Reviews
from api.serializers import BooksSerializer,BooksModelSerializer,UserSerializer,CartSerializer,ReviewSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework import authentication,permissions

class Bookview(APIView):
    def get(self,request,*args,**kwargs):
        qs=Books.objects.all()
        serializer=BooksSerializer(qs,many=True)
        return Response(data=serializer.data)

    def post(self,request,*args,**kwargs):
        serializer=BooksSerializer(data=request.data)
        if serializer.is_valid():
            Books.objects.create(**serializer.validated_data)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)


class BookDetailView(APIView):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("id")
        qs=Books.objects.get(id=id)
        serializer=BooksSerializer(qs,many=False)
        return Response(data=serializer.data)
    def put(self,request,*args,**kwargs):
        id=kwargs.get("id")
        Books.objects.filter(id=id).update(**request.data)
        qs=Books.objects.get(id=id)
        serializer=BooksSerializer(qs,many=False)
        return Response(data=serializer.data)
    def delete(self,request,*args,**kwargs):
        id=kwargs.get("id")
        Books.objects.filter(id=id).delete()
        return Response(data="object deleted")

#viewSets

# class BookViewsetView(viewsets.ViewSet):
#     def list(self,request,*args,**kwargs):
#         qs=Books.objects.all()
#         serializers=BooksSerializer(qs,many=True)
#         return  Response(data=serializers.data)
#
#     def create(self,request,*args,**kwargs):
#         serializer=BooksModelSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data=serializer.data)
#         else:
#             return Response(data=serializer.errors)
#
#     def retrieve(self,request,*args,**kwargs):
#         id=kwargs.get("pk")
#         qs=Books.objects.get(id=id)
#         serializer=BooksModelSerializer(qs,many=False)
#         return Response(data=serializer.data)
#
#     def destroy(self,request,*args,**kwargs):
#         id=kwargs.get("pk")
#         Books.objects.filter(id=id).delete()
#         return Response (data="delete")
#
#     def update(self,request,*args,**kwargs):
#         id=kwargs.get("pk")
#         obj=Books.object.get(id=id)
#         serializer=BooksModelSerializer(data=request.data,instance=obj)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data=serializer.data)
#         else:
#             return Response(data=serializer.errors)

# class UsersView(viewsets.ViewSet):
#
#     def create(self,request,*args,**kwargs):
#         serializer=UserSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data=serializer.data)
#         else:
#             return Response(data=serializer.errors)

#ModelViewset

class BookViewsetView(viewsets.ModelViewSet):
    serializer_class = BooksModelSerializer
    queryset = Books.objects.all()
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=["GET"], detail=False)
    def categories(self, request, *args, **kwargs):
        res = Books.objects.values_list('category', flat=True).distinct()
        return Response(data=res)

    @action(methods=["POST"], detail=True)
    def addto_cart(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        item = Books.objects.get(id=id)
        user = request.user
        user.carts_set.create(book=item)
        return Response(data="item added to cart")

    @action(methods=["POST"], detail=True)
    def add_review(self, request, *args, **kwargs):
        user = request.user
        id = kwargs.get("pk")
        object = Books.objects.get(id=id)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(book=object, user=user)
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)

    @action(methods=["GET"], detail=True)
    def reviews(self, request, *args, **kwargs):
        product = self.get_object()
        qs = product.reviews_set.all()
        serializer = ReviewSerializer(qs, many=True)
        return Response(data=serializer.data)


class CartsView(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Carts.objects.all()
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Carts.objects.filter(user=self.request.user)

    # def list(self,request,*args,**kwargs):
    #     qs=request.user.carts_set.all()
    #     serializer=CartSerializer(qs,many=True)
    #     return Response(data=serializer.data)


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ReviewDeleteView(APIView):
    def delete(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        Reviews.objects.filter(id=id).delete()
        return Response(data="review deleted")

