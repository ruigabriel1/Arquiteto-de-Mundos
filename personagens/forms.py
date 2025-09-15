from django import forms
from django.contrib.auth.models import User
from campanhas.models import Campanha
from .models import Personagem
from sistema_unificado.models import SistemaJogo, ConteudoSistema


class PersonagemForm(forms.ModelForm):
    """Formulário para criação e edição de personagens."""
    
    class Meta:
        model = Personagem
        fields = [
            'nome', 'campanha', 'sistema_jogo',
            'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma',
            'historia', 'personalidade', 'avatar'
        ]
        
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do personagem'
            }),
            'campanha': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sistema_jogo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'forca': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 20,
                'value': 10
            }),
            'destreza': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 20,
                'value': 10
            }),
            'constituicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 20,
                'value': 10
            }),
            'inteligencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 20,
                'value': 10
            }),
            'sabedoria': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 20,
                'value': 10
            }),
            'carisma': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 3,
                'max': 20,
                'value': 10
            }),
            'historia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'História de fundo do personagem...'
            }),
            'personalidade': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Traços de personalidade, ideais, vínculos...'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        
        labels = {
            'nome': 'Nome do Personagem',
            'campanha': 'Campanha',
            'sistema_jogo': 'Sistema de Jogo',
            'forca': 'Força',
            'destreza': 'Destreza',
            'constituicao': 'Constituição',
            'inteligencia': 'Inteligência',
            'sabedoria': 'Sabedoria',
            'carisma': 'Carisma',
            'historia': 'História de Fundo',
            'personalidade': 'Personalidade',
            'avatar': 'Avatar (Opcional)'
        }
        
        help_texts = {
            'nome': 'Digite o nome do seu personagem',
            'avatar': 'Imagem do personagem (JPG, PNG ou GIF, máx. 5MB)',
            'forca': 'Valor entre 3 e 20',
            'destreza': 'Valor entre 3 e 20',
            'constituicao': 'Valor entre 3 e 20',
            'inteligencia': 'Valor entre 3 e 20',
            'sabedoria': 'Valor entre 3 e 20',
            'carisma': 'Valor entre 3 e 20'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar campanhas para mostrar apenas as do usuário
        if user:
            self.fields['campanha'].queryset = Campanha.objects.filter(organizador=user)
        else:
            self.fields['campanha'].queryset = Campanha.objects.none()
        
        # Configurar campos como opcionais se necessário
        self.fields['historia'].required = False
        self.fields['personalidade'].required = False
        self.fields['avatar'].required = False

    def clean_nome(self):
        """Validar nome do personagem."""
        nome = self.cleaned_data.get('nome')
        if not nome or not nome.strip():
            raise forms.ValidationError('Nome do personagem é obrigatório.')
        
        if len(nome.strip()) < 2:
            raise forms.ValidationError('Nome deve ter pelo menos 2 caracteres.')
            
        return nome.strip()

    def clean_avatar(self):
        """Validar upload do avatar."""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Verificar tamanho (máx 5MB)
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Tamanho máximo do arquivo é 5MB.')
            
            # Verificar tipo de arquivo
            valid_types = ['image/jpeg', 'image/png', 'image/gif']
            if avatar.content_type not in valid_types:
                raise forms.ValidationError('Apenas arquivos JPG, PNG ou GIF são permitidos.')
        
        return avatar

    def clean(self):
        """Validações gerais do formulário."""
        cleaned_data = super().clean()
        
        return cleaned_data


class PersonagemAvancadoForm(forms.ModelForm):
    """Formulário avançado para o construtor step-by-step."""
    
    # Campos adicionais para o construtor
    sistema_slug = forms.CharField(max_length=20, required=True)
    raca_dados = forms.CharField(widget=forms.HiddenInput(), required=False)
    classe_dados = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Personagem
        fields = [
            'nome', 'campanha', 'sistema_jogo',
            'forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma',
            'historia', 'personalidade', 'avatar'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['campanha'].queryset = Campanha.objects.filter(organizador=user)
        else:
            self.fields['campanha'].queryset = Campanha.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        
        # Processar dados adicionais do construtor
        sistema_slug = cleaned_data.get('sistema_slug')
        raca_dados = cleaned_data.get('raca_dados')
        classe_dados = cleaned_data.get('classe_dados')
        
        # Converter de JSON se necessário
        import json
        if raca_dados:
            try:
                cleaned_data['raca_info'] = json.loads(raca_dados)
            except json.JSONDecodeError:
                pass
                
        if classe_dados:
            try:
                cleaned_data['classe_info'] = json.loads(classe_dados)
            except json.JSONDecodeError:
                pass
        
        return cleaned_data