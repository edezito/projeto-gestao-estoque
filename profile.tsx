import { useState } from 'react'; // ✅ ADICIONE ESTA LINHA  
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { User, AlertTriangle } from 'lucide-react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { useAuth } from '@/contexts/AuthContext';
import { usersAPI } from '@/api';
import { toast } from 'sonner';

export default function Profile() {
  const navigate = useNavigate();
  const { seller, logout, updateSeller } = useAuth();
  const [formData, setFormData] = useState({
    nome: seller?.nome || '',
    cnpj: seller?.cnpj || '',
    email: seller?.email || '',
    celular: seller?.celular || '',
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => 
      usersAPI.update(id, data),
    onSuccess: (data) => {
      updateSeller(data.usuario || data);
      toast.success('Perfil atualizado com sucesso!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.erro || 'Erro ao atualizar perfil');
    },
  });

  const inactivateMutation = useMutation({
    mutationFn: usersAPI.inactivate,
    onSuccess: () => {
      toast.success('Conta inativada com sucesso');
      logout();
      navigate('/auth/login');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.erro || 'Erro ao inativar conta');
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!seller) return;

    updateMutation.mutate({ id: seller.id, data: formData });
  };

  const handleInactivate = () => {
    if (!seller) return;
    inactivateMutation.mutate(seller.id);
  };

  if (!seller) {
    return (
      <div className="min-h-screen bg-secondary/30">
        <Navbar />
        <div className="container mx-auto px-4 py-8 text-center">
          <p>Usuário não encontrado</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary/30">
      <Navbar />

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Meu Perfil</h1>
          <p className="text-muted-foreground">Gerencie suas informações pessoais</p>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Informações do Usuário
            </CardTitle>
            <CardDescription>Atualize seus dados cadastrais</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome</Label>
                <Input
                  id="nome"
                  name="nome"
                  value={formData.nome}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cnpj">CNPJ</Label>
                <Input
                  id="cnpj"
                  name="cnpj"
                  value={formData.cnpj}
                  onChange={handleChange}
                  required
                  disabled // CNPJ geralmente não pode ser alterado
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">E-mail</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="celular">Celular</Label>
                <Input
                  id="celular"
                  name="celular"
                  value={formData.celular}
                  onChange={handleChange}
                  required
                />
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Salvando...' : 'Salvar Alterações'}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              Zona de Perigo
            </CardTitle>
            <CardDescription>
              Ações irreversíveis que afetarão sua conta
            </CardDescription>
          </CardHeader>
          <CardContent>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button 
                  variant="destructive" 
                  className="w-full"
                  disabled={inactivateMutation.isPending}
                >
                  {inactivateMutation.isPending ? 'Inativando...' : 'Inativar Conta'}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Tem certeza?</AlertDialogTitle>
                  <AlertDialogDescription>
                    Esta ação irá inativar sua conta. Você precisará entrar em contato
                    com o suporte para reativá-la.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleInactivate}
                    className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  >
                    Confirmar Inativação
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}