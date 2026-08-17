from django import forms
from .models import Nilai
from core.models import Disposisi

class NilaiForm(forms.ModelForm):
    class Meta:
        model = Nilai
        fields = ['surat', 'kriteria', 'nilai']
        widgets = {
            'surat': forms.Select(attrs={
                'class': 'form-select rounded p-2 w-1/4',
            }),
            'kriteria': forms.Select(attrs={
                'class': 'form-select rounded p-2 w-1/4',
            }),
            'nilai': forms.NumberInput(attrs={
                'class': 'border rounded p-2 w-1/4',
                'placeholder': 'Masukkan Nilai'
            }),
        }

class DisposisiForm(forms.ModelForm):
    class Meta:
        model = Disposisi
        fields = ['catatan', 'tujuan']
        widgets = {
            'catatan': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Masukkan catatan'
            }),
            'tujuan': forms.Select(attrs={
                'class': 'border rounded p-2 w-full',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tujuan wajib dipilih
        self.fields['tujuan'].required = True

        # Ganti teks pilihan kosong
        choices = list(self.fields['tujuan'].choices)

        if choices and choices[0][0] == '':
            choices[0] = ('', 'Pilih tujuan')

        self.fields['tujuan'].choices = choices