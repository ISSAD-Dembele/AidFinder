import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import userService from '@/src/services/user'
import { getApiErrorMessage } from '@/src/utils/errors'

/** Page changement de mot de passe — connectée à PATCH /users/change-password */
export default function ChangePassword() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    current_password: '',
    new_password: '',
    confirm_new_password: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }))
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (form.new_password !== form.confirm_new_password) {
      setError('Les mots de passe ne correspondent pas.')
      return
    }

    setLoading(true)
    try {
      const data = await userService.changePassword(form)
      setSuccess(data.message)
      setForm({ current_password: '', new_password: '', confirm_new_password: '' })
      setTimeout(() => navigate('/dashboard/profil'), 2000)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Impossible de changer le mot de passe.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-1 items-center justify-center px-4 py-8 sm:px-6">
      <div className="w-full max-w-md">
        <Link
          to="/dashboard/profil"
          className="mb-6 inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="size-4" />
          Retour au profil
        </Link>

        <Card className="border-border/60 shadow-lg">
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Changer le mot de passe</CardTitle>
            <CardDescription>
              Assurez la sécurité de votre compte en utilisant un mot de passe fort
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-lg bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              )}
              {success && (
                <div className="rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
                  {success}
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="current_password">Mot de passe actuel</Label>
                <Input
                  id="current_password"
                  name="current_password"
                  type="password"
                  value={form.current_password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="new_password">Nouveau mot de passe</Label>
                <Input
                  id="new_password"
                  name="new_password"
                  type="password"
                  value={form.new_password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm_new_password">Confirmer le mot de passe</Label>
                <Input
                  id="confirm_new_password"
                  name="confirm_new_password"
                  type="password"
                  value={form.confirm_new_password}
                  onChange={handleChange}
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-[#2963E8] hover:bg-[#1e52c7]"
                disabled={loading}
              >
                {loading ? 'Enregistrement...' : 'Enregistrer la modification'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
