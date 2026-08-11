from django import forms
from .models import Surat, Perihal, Status, Kriteria, Sifat, Sumbersurat, Pengirim

class SuratForm(forms.ModelForm):
    perihal = forms.ModelChoiceField(
        queryset=Perihal.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 w-full border rounded focus:outline-none focus:ring-2 focus:ring-yellow-500'
        })
    )

    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500'
        })
    )

    sifat = forms.ModelChoiceField(
        queryset=Sifat.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500'
        })
    )

    pengirim = forms.ModelChoiceField(
        queryset=Pengirim.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500'
        })
    )

    sumber_surat = forms.ModelChoiceField(
        queryset=Sumbersurat.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select2 w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-yellow-500'
        })
    )

    tanggal_surat = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'border rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-yellow-500'
        }),
        required=True,
        label="Tanggal Surat"
    )

    class Meta:
        model = Surat
        fields = ['no_surat', 'tanggal_surat', 'perihal', 'pengirim', 'sumber_surat', 'keterangan', 'status', 'sifat', 'file']

        widgets = {
            'no_surat': forms.TextInput(attrs={'class': 'border rounded p-2 w-full'}),
            'keterangan': forms.Textarea(attrs={'class': 'border rounded p-2 w-full'}),
            'file': forms.FileInput(attrs={'class': 'border rounded p-2 w-full'}),
        }

class PerihalForm(forms.ModelForm):
    class Meta:
        model = Perihal
        fields = ['hal']    

        widgets = {
            'hal': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['nama']    

        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control'}),
        }

class KriteriaForm(forms.ModelForm):
    class Meta:
        model = Kriteria
        fields = ['nama', 'bobot']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Masukkan Nama Kriteria'
            }),
            'bobot': forms.NumberInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Masukkan Bobot Kriteria'
            }),
        }

    def clean_bobot(self):
        bobot = self.cleaned_data.get('bobot')
        if bobot is None:
            raise forms.ValidationError("Bobot wajib diisi.")
        if bobot <= 0:
            raise forms.ValidationError("Bobot harus lebih besar dari 0.")
        return bobot

class SifatForm(forms.ModelForm):
    class Meta:
        model = Sifat
        fields = ['nama']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Masukkan Sifat'
            }),
        }

class SumbersuratForm(forms.ModelForm):
    class Meta:
        model = Sumbersurat
        fields = ['nama']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Masukkan Sumber Surat'
            }),
        }

class PengirimForm(forms.ModelForm):
    class Meta:
        model = Pengirim
        fields = ['nama']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'border rounded p-2 w-full',
                'placeholder': 'Masukkan Pengirim'
            }),
        }
