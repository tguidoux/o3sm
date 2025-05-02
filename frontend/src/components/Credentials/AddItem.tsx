import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { useState } from "react"
import {
  type ApiError,
  type CredentialCreate,
  type CredentialPublic,
  CredentialsService,
  OpenAPI,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddCredentialProps {
  isOpen: boolean
  onClose: () => void
}

const AddItem = ({ isOpen, onClose }: AddCredentialProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const [created, setCreated] = useState(false)
  const [newCredential, setNewCredential] = useState<CredentialPublic>()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<CredentialCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {},
  })

  const mutation = useMutation({
    mutationFn: (data: CredentialCreate) =>
      CredentialsService.createCredential({ requestBody: data }),
    onSuccess: (data) => {
      showToast("Success!", "Credential created successfully.", "success")
      setCreated(true)
      setNewCredential(data)
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["credentials"] })
    },
  })

  const onSubmit: SubmitHandler<CredentialCreate> = (data) => {
    mutation.mutate(data)
  }

  const onCustomClose = () => {
    setCreated(false)
    setNewCredential(undefined)
    onClose()
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onCustomClose}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>New Credential</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {created ? (
              newCredential ? (
                <>
                  <p>
                    <b>Access Key ID</b>
                  </p>
                  <code>{newCredential.access_key}</code>
                  <br />
                  <br />
                  <p>
                    <b>Secret Access Key</b>
                  </p>
                  <code>{newCredential.secret_key}</code>
                  <br />
                  <br />
                  <p>
                    <b>Easy cli setup</b>
                  </p>
                  <code>
                    {`export AWS_ACCESS_KEY_ID=\"${newCredential.access_key}\"\n`}
                    <br />
                    {`export AWS_SECRET_ACCESS_KEY=\"${newCredential.secret_key}\"\n`}
                    <br />
                    {'export AWS_DEFAULT_REGION=""'}
                    <br />
                    {`export AWS_ENDPOINT_URL=\"${OpenAPI.BASE}\"`}
                  </code>
                </>
              ) : (
                <p>Failed to create credential.</p>
              )
            ) : (
              <p>Are you sure you want to create credential?</p>
            )}
          </ModalBody>

          <ModalFooter gap={3}>
            {!created && (
              <Button variant="primary" type="submit" isLoading={isSubmitting}>
                Yes
              </Button>
            )}
            <Button onClick={onCustomClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default AddItem
