from django.shortcuts import render
from .forms import *
from .models import *
from .utils import blastn, blastp
from django.http import HttpRequest, JsonResponse
import threading
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.password_validation import validate_password as v_p
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request: HttpRequest):
    return render(request, 'bacterial_genome_annotation/home.html')

def AddGenome(request: HttpRequest):
    return render(request, 'bacterial_genome_annotation/AddGenome.html')

@login_required
def Account(request: HttpRequest):
    return render(request, 'bacterial_genome_annotation/Account.html')

def LoginPage(request: HttpRequest):
    return render(request, 'bacterial_genome_annotation/LoginPage.html')

def annoter(request: HttpRequest):
    form = AnnotForm()
    description = 'empty'
    #sequences = []
    if request.method == "POST":
        form = AnnotForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['ID']
            gene = form.cleaned_data['gene name']
            gene_biotype = form.cleaned_data['gene_biotype']
            transcript_biotype = form.cleaned_data['biotype transcript_name']
            gene_symbol = form.cleaned_data['gene symbol']
            description = form.cleaned_data['description']
            transcript = form.cleaned_data['transcript']
            isValidate = form.cleaned_data['isValidate']

            # Querry
            #sequences = Sequence.objects.all()
            #if bacterial_name!='':
            #    sequences = sequences.filter(genome__id__contains=bacterial_name)
            #if isCds:
            #    sequences = sequences.filter(isCds=isCds)
            #if gene_name!='':
            #    sequences = sequences.filter(annotationQueryName__isValidate=True, annotationQueryName__gene__contains=gene_name)
            #if transcript_name!='':
            #    sequences = sequences.filter(annotationQueryName__isValidate=True, annotationQueryName__transcript__contains=transcript_name)
            #if description!='':
            #    sequences = sequences.filter(annotationQueryName__isValidate=True, annotationQueryName__description__contains=description)
            #if seq!='':
            #    sequences = sequences.filter(sequence__regex='.*'+'.*'.join(seq.split('%'))+'.*')
    return render(request, 'bacterial_genome_annotation/annoter.html', {"form": form, "description": description})#, "sequences": sequences})

#
#### ANNOT via la page sequence ref BLAST #####
#
def ANNOT(request: HttpRequest,id):
    form = AnnotForm()
    description = 'empty'
    #sequences = []
    if request.method == "POST":
        form = AnnotForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data['ID']
            gene = form.cleaned_data['gene name']
            gene_biotype = form.cleaned_data['gene_biotype']
            transcript_biotype = form.cleaned_data['biotype transcript_name']
            gene_symbol = form.cleaned_data['gene symbol']
            description = form.cleaned_data['description']
            transcript = form.cleaned_data['transcript']
            isValidate = form.cleaned_data['isValidate']

    return render(request, 'bacterial_genome_annotation/annoter.html', {"form": form, "description": description})#, "sequences": sequences})

@login_required
def Parser(request: HttpRequest, id):
    params = {"progression": "", "results": []}
    if id!='0':
        query = BlastResult.objects.filter(id=id)
        if not query:
            sequence = Sequence.objects.get(id=id)
            blast = BlastResult()
            blast.id = id
            blast.isCds = sequence.isCds
            blast.sequence = sequence.sequence
            blast.save()
            if sequence.isCds:
                thread = threading.Thread(target=blastn, args=(blast,))
                thread.start()
            else:
                thread = threading.Thread(target=blastp, args=(blast,))
                thread.start()
        else:
            list = BlastHit.objects.filter(blastResult__id=id)
            if not list:
                if not BlastResult.objects.get(id=id):
                    params['progression'] = 'Something went wrong'
                else:
                    params['progression'] = 'Still in progress'
            else:
                params['progression'] = 'Finished !'
                params['results'] = list
            
    return render(request, 'bacterial_genome_annotation/Parser.html', params)

def Search(request: HttpRequest):
    form = SearchForm()
    description = 'empty'
    sequences = []
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            bacterial_name = form.cleaned_data['bacterial_name']
            isCds = form.cleaned_data['nucleic_or_peptidic']
            gene_name = form.cleaned_data['gene_name']
            transcript_name = form.cleaned_data['transcript_name']
            description = form.cleaned_data['description']
            seq = form.cleaned_data['sequence']
            # Querry
            sequences = Sequence.objects.all()
            if bacterial_name!='':
                sequences = sequences.filter(genome__id__icontains=bacterial_name)
            if isCds:
                sequences = sequences.filter(isCds=isCds)
            if gene_name!='':
                sequences = sequences.filter(annotationQueryName__isValidate=True, annotationQueryName__gene__icontains=gene_name)
            if transcript_name!='':
                sequences = sequences.filter(annotationQueryName__isValidate=True, annotationQueryName__transcript__icontains=transcript_name)
            if description!='':
                sequences = sequences.filter(annotationQueryName__isValidate=True, annotationQueryName__description__icontains=description)
            if seq!='':
                seq = seq.upper()
                splitSearch = seq.split('%')
                for s in splitSearch:
                    sequences = sequences.filter(sequence__contains=s)
                sequences = sequences.filter(sequence__regex='.*'+'.*'.join(splitSearch)+'.*')
    return render(request, 'bacterial_genome_annotation/search.html', {"form": form, "description": description, "sequences": sequences})

def SequenceView(request: HttpRequest, id):
    
    sequence = Sequence.objects.get(id=id)
    annotationsValidated = Annotation.objects.filter(sequence=sequence, isValidate=True)
    annotations = Annotation.objects.filter(sequence=sequence, isValidate=False)
    form = CommentForm()
    """
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            newComment = Comment()
            newComment.annotation = annotationsValidated.first()
            newComment.user = request.user
            newComment.content = form.cleaned_data['comment']
            newComment.save()
    class annotForTheme:
        def __init__(self, ann: Annotation, com: list):
            self.annotation=ann
            self.comments = com
            
    class commentForTheme:
        def __init__(self, com: Comment, ans: list):
            self.comment = com
            self.answers = ans
    
    annotationsValidatedBetter = []
    for a in annotationsValidated:
        comments = Comment.objects.filter(annotation=a)
        answers = comments.filter(isAnswer=True)
        base = comments.filter(isAnswer = False).order_by('-likes')
        commentsPretty = []
        for c in base:
            alist = []
            current = c
            nextAnswer = answers.filter(question=current).order_by('date')
            while not (not nextAnswer):
                alist.append(nextAnswer.first())
                current = nextAnswer
                nextAnswer = answers.filter(question=current)
            commentsPretty.append(commentForTheme(c, alist))
        annotationsValidatedBetter.append(annotForTheme(a, commentsPretty))
        
    annotationsBetter = []
    for a in annotations:
        comments = Comment.objects.filter(annotation=a)
        answers = comments.filter(isAnswer=True)
        base = comments.filter(isAnswer = False).order_by('-likes')
        commentsPretty = []
        for c in base:
            alist = []
            current = c
            nextAnswer = answers.filter(question=current).order_by('date')
            while not (not nextAnswer):
                alist.append(nextAnswer.first())
                current = nextAnswer
                nextAnswer = answers.filter(question=current)
            commentsPretty.append(commentForTheme(c, alist))
        annotationsBetter.append(annotForTheme(a, commentsPretty))"""
        
    params = {
        "seq":sequence,
        "annotationsValidated":annotationsValidated,
        "annotations":annotations,
        "form": form
    }
    return render(request, 'bacterial_genome_annotation/sequence.html', params)

class SignUpView(generic.CreateView):
    template_name = 'bacterial_genome_annotation/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid
    
def validate_email(request: HttpRequest):
    """Check email availability"""
    email = request.POST.get('email', '')
    response = {
        'is_empty': email=='',
        'is_taken': User.objects.filter(email__iexact=email).exists(),
        'is_valid': bool(re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', email))
    }
    return JsonResponse(response)

def validate_password(request: HttpRequest):
    password = request.POST.get('password1', None)
    try:
        v_p(password)
        return JsonResponse({'is_valid': True, 'message': 'Password is valid', 'is_empty': password==''})
    except ValidationError as e:
        return JsonResponse({'is_valid': False, 'message': ' '.join(e.messages), 'is_empty': password==''})
    
def contact(request: HttpRequest):
    return render(request, 'bacterial_genome_annotation/contact.html')

def AboutUs(request: HttpRequest):
    return render(request, 'bacterial_genome_annotation/AboutUs.html')
