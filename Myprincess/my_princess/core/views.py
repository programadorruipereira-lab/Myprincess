from django.shortcuts import render, redirect, get_object_or_404
from django.apps import apps
from django.views.decorators.http import require_POST
from .models import Despesa, Receita, Dieta, CicloMenstrual, Hidratacao, Gravidez, Livro, EntradaDiario, Perfil

@require_POST
def delete_item(request, model_name, item_id):
    try:
        model = apps.get_model('core', model_name)
        item = get_object_or_404(model, id=item_id)
        item.delete()
    except LookupError:
        pass # Handle gracefully or show error
    
    # Redirect back to the previous page or a default
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@require_POST
def reset_hidratacao(request):
    hoje = timezone.localdate()
    Hidratacao.objects.filter(data=hoje).update(copos_bebidos=0)
    return redirect('hidratacao')

@require_POST
def update_livro_status(request, livro_id):
    novo_status = request.POST.get('status')
    livro = get_object_or_404(Livro, id=livro_id)
    livro.status = novo_status
    livro.save()
    return redirect('leitura')

def dashboard(request):
    # Hydration
    hoje = timezone.localdate()
    hidra, _ = Hidratacao.objects.get_or_create(data=hoje)
    
    # Menstruation
    ciclos = CicloMenstrual.objects.all().order_by('-data_inicio')
    proxima = "N/A"
    if ciclos.exists():
        proxima = (ciclos.first().data_inicio + timedelta(days=28)).strftime('%d/%m')

    # Financial Balance (Monthly)
    from django.db.models import Sum
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    total_receitas = Receita.objects.filter(data__month=mes_atual, data__year=ano_atual).aggregate(Sum('valor'))['valor__sum'] or 0
    total_despesas = Despesa.objects.filter(data__month=mes_atual, data__year=ano_atual).aggregate(Sum('valor'))['valor__sum'] or 0
    saldo_mes = total_receitas - total_despesas

    return render(request, 'core/dashboard.html', {
        'copos': hidra.copos_bebidos,
        'meta_copos': hidra.meta_copos,
        'proxima_menstruacao': proxima,
        'saldo_mes': saldo_mes
    })

from .models import Despesa, Receita
from django.utils import timezone
from operator import itemgetter

def financeiro(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        descricao = request.POST.get('descricao')
        categoria = request.POST.get('categoria')
        valor = request.POST.get('valor')
        data = request.POST.get('data')

        if tipo == 'despesa':
            Despesa.objects.create(descricao=descricao, categoria=categoria, valor=valor, data=data)
        elif tipo == 'receita':
            Receita.objects.create(descricao=descricao, categoria=categoria, valor=valor, data=data)

    despesas = list(Despesa.objects.all().values())
    for d in despesas: d['tipo'] = 'despesa'
    
    receitas = list(Receita.objects.all().values())
    for r in receitas: r['tipo'] = 'receita'

    transacoes = sorted(despesas + receitas, key=itemgetter('data'), reverse=True)

    return render(request, 'core/financeiro.html', {
        'transacoes': transacoes,
        'today': timezone.localdate().strftime('%Y-%m-%d')
    })

from .models import Dieta, CicloMenstrual, Hidratacao, Gravidez, Livro, EntradaDiario

def dieta(request):
    perfil = Perfil.objects.first()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'registrar_refeicao':
            refeicao = request.POST.get('refeicao')
            alimentos = request.POST.get('alimentos')
            observacoes = request.POST.get('observacoes')
            Dieta.objects.create(refeicao=refeicao, alimentos=alimentos, observacoes=observacoes)
        
        elif action == 'salvar_perfil':
            nome = request.POST.get('nome')
            altura = float(request.POST.get('altura'))
            peso = float(request.POST.get('peso'))
            fase = request.POST.get('fase')
            objetivo = request.POST.get('objetivo')
            data_nascimento = request.POST.get('data_nascimento')
            
            if perfil:
                perfil.nome = nome
                perfil.altura = altura
                perfil.peso = peso
                perfil.fase_vida = fase
                perfil.objetivo = objetivo
                perfil.data_nascimento = data_nascimento
                perfil.save()
            else:
                Perfil.objects.create(nome=nome, altura=altura, peso=peso, fase_vida=fase, objetivo=objetivo, data_nascimento=data_nascimento)
            perfil = Perfil.objects.first() # Reload

    # Calculate BMI
    imc = 0
    classificacao_imc = ""
    dieta_sugerida = ""

    if perfil:
        imc = perfil.peso / (perfil.altura * perfil.altura)
        if imc < 18.5: classificacao_imc = "Abaixo do peso"
        elif imc < 25: classificacao_imc = "Peso ideal"
        elif imc < 30: classificacao_imc = "Sobrepeso"
        else: classificacao_imc = "Obesidade"

        # Simple Rule-based "AI" Plan
        if perfil.fase_vida == 'Gestante':
            dieta_sugerida = "Foco em ácido fólico, ferro e cálcio. Aumente levemente as calorias com frutas e integrais."
        elif perfil.objetivo and 'emagrecer' in perfil.objetivo.lower():
            dieta_sugerida = "Priorize proteínas magras e vegetais. Reduza carboidratos simples à noite."
        else:
            dieta_sugerida = "Mantenha uma alimentação balanceada com frutas, legumes e hidratação constante."

    items = Dieta.objects.filter(data=timezone.localdate()).order_by('-id')
    
    return render(request, 'core/dieta.html', {
        'dieta_items': items,
        'perfil': perfil,
        'imc': round(imc, 2),
        'classificacao_imc': classificacao_imc,
        'dieta_sugerida': dieta_sugerida
    })

from datetime import timedelta

def menstruacao(request):
    if request.method == 'POST':
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim') or None
        sintomas = request.POST.get('sintomas')
        CicloMenstrual.objects.create(data_inicio=data_inicio, data_fim=data_fim, sintomas=sintomas)

    ciclos = CicloMenstrual.objects.all().order_by('-data_inicio')
    
    # Prediction Logic
    proxima_menstruacao = None
    periodo_fertil_inicio = None
    periodo_fertil_fim = None
    
    if ciclos.exists():
        ultimo_ciclo = ciclos.first()
        # Assuming 28 days cycle
        proxima_menstruacao = ultimo_ciclo.data_inicio + timedelta(days=28)
        # Fertile period: 10 to 14 days after start (rough estimate)
        periodo_fertil_inicio = ultimo_ciclo.data_inicio + timedelta(days=10)
        periodo_fertil_fim = ultimo_ciclo.data_inicio + timedelta(days=14)

    return render(request, 'core/menstruacao.html', {
        'ciclos': ciclos,
        'proxima_menstruacao': proxima_menstruacao,
        'periodo_fertil_inicio': periodo_fertil_inicio,
        'periodo_fertil_fim': periodo_fertil_fim
    })

def hidratacao(request):
    hoje = timezone.localdate()
    registro, created = Hidratacao.objects.get_or_create(data=hoje)

    if request.method == 'POST':
        registro.copos_bebidos += 1
        registro.save()
    
    atingiu_meta = registro.copos_bebidos >= registro.meta_copos
    return render(request, 'core/hidratacao.html', {
        'copos_hoje': registro.copos_bebidos,
        'meta': registro.meta_copos,
        'atingiu_meta': atingiu_meta
    })

def gravidez(request):
    if request.method == 'POST':
        semanas = request.POST.get('semanas')
        notas = request.POST.get('notas')
        humor = request.POST.get('humor')
        Gravidez.objects.create(semanas_gestacao=semanas, notas_medicas=notas, humor=humor)
    
    registros = Gravidez.objects.all().order_by('-id')
    return render(request, 'core/gravidez.html', {'registros': registros})

def leitura(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')
        status = request.POST.get('status')
        Livro.objects.create(titulo=titulo, autor=autor, status=status)
    
    livros = Livro.objects.all().order_by('-id')
    return render(request, 'core/leitura.html', {'livros': livros})

def diario(request):
    if request.method == 'POST':
        conteudo = request.POST.get('conteudo')
        humor = request.POST.get('humor')
        EntradaDiario.objects.create(conteudo=conteudo, humor=humor)

    entradas = EntradaDiario.objects.all().order_by('-data')
    return render(request, 'core/diario.html', {'entradas': entradas})
