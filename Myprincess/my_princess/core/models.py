from django.db import models
from django.utils import timezone

class Despesa(models.Model):
    descricao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()

    class Meta:
        db_table = 'Despesas'

    def __str__(self):
        return f"{self.descricao} - {self.valor}"

class Receita(models.Model):
    descricao = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()

    class Meta:
        db_table = 'Receitas'

    def __str__(self):
        return f"{self.descricao} - {self.valor}"

class Dieta(models.Model):
    REFEICAO_CHOICES = [
        ('Cafe', 'Café da Manhã'),
        ('Almoco', 'Almoço'),
        ('Jantar', 'Jantar'),
        ('Lanche', 'Lanche'),
    ]
    refeicao = models.CharField(max_length=50, choices=REFEICAO_CHOICES)
    alimentos = models.TextField()
    observacoes = models.TextField(blank=True, null=True)
    data = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'Dieta'

    def __str__(self):
        return f"{self.refeicao} - {self.data}"

class CicloMenstrual(models.Model):
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    sintomas = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'CiclosMenstruais'
    
    def __str__(self):
        return f"Ciclo {self.data_inicio}"

class Hidratacao(models.Model):
    copos_bebidos = models.IntegerField(default=0)
    meta_copos = models.IntegerField(default=8)
    data = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'Hidratacao'

    def __str__(self):
        return f"{self.data} - {self.copos_bebidos}/{self.meta_copos}"

class Gravidez(models.Model):
    semanas_gestacao = models.IntegerField()
    notas_medicas = models.TextField(blank=True, null=True)
    humor = models.CharField(max_length=50, blank=True, null=True) # Emojis or text
    data_importante = models.DateField(blank=True, null=True)
    descricao_data = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Gravidez'

    def __str__(self):
        return f"Semana {self.semanas_gestacao} - {self.humor}"

class Perfil(models.Model):
    nome = models.CharField(max_length=100)
    altura = models.FloatField(help_text="Altura em metros")
    peso = models.FloatField(help_text="Peso em kg")
    data_nascimento = models.DateField()
    fase_vida = models.CharField(max_length=50, choices=[
        ('Normal', 'Normal'),
        ('Gestante', 'Gestante'),
        ('Tentante', 'Tentante'),
        ('Lactante', 'Lactante'),
    ], default='Normal')
    objetivo = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Perfil'

    def __str__(self):
        return self.nome

class Livro(models.Model):
    STATUS_CHOICES = [
        ('Lendo', 'Lendo'),
        ('Lido', 'Lido'),
        ('Quero Ler', 'Quero Ler'),
    ]
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    class Meta:
        db_table = 'Livros'

    def __str__(self):
        return self.titulo

class EntradaDiario(models.Model):
    conteudo = models.TextField()
    data = models.DateTimeField(default=timezone.now)
    humor = models.CharField(max_length=50, blank=True, null=True) # Emojis

    class Meta:
        db_table = 'EntradaDiario'

    def __str__(self):
        return f"Diário {self.data} - {self.humor}"
