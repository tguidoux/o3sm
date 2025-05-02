import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
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

import {
  type ApiError,
  type ParameterPublic,
  ParametersService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { handleError } from "../../utils"

interface AddParameterProps {
  isOpen: boolean
  onClose: () => void
}

const AddItem = ({ isOpen, onClose }: AddParameterProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ParameterPublic>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      Name: "",
      Value: "",
      Type: "String",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: ParameterPublic) =>
      ParametersService.createParameter({ requestBody: data }),
    onSuccess: () => {
      showToast("Success!", "Item created successfully.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["parameters"] })
    },
  })

  const onSubmit: SubmitHandler<ParameterPublic> = (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Add Parameter</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.Name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="name"
                {...register("Name", {
                  required: "Name is required.",
                })}
                placeholder="Name"
                type="text"
              />
              {errors.Name && (
                <FormErrorMessage>{errors.Name.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl isRequired mt={4}>
              <FormLabel htmlFor="value">Value</FormLabel>
              <Input
                id="value"
                {...register("Value", {
                  required: "Value is required.",
                })}
                placeholder="Value"
                type="text"
              />
            </FormControl>
            <FormControl isRequired mt={4}>
              <FormLabel htmlFor="type">Type</FormLabel>
              <Input
                id="type"
                {...register("Type", {
                  required: "Type is required.",
                })}
                placeholder="Type"
                type="text"
                defaultValue={"String"}
              />
            </FormControl>
          </ModalBody>

          <ModalFooter gap={3}>
            <Button variant="primary" type="submit" isLoading={isSubmitting}>
              Save
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default AddItem
