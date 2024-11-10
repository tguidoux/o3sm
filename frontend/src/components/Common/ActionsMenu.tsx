import {
  Button,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  useDisclosure,
} from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { ItemPublic, UserPublic, CredentialPublic, ParameterPublic } from "../../client"
import EditUser from "../Admin/EditUser"
import EditItem from "../Items/EditItem"
import EditParameter from "../Parameters/EditParameter"
import Delete from "./DeleteAlert"

interface ActionsMenuProps {
  type: string
  value: ItemPublic | UserPublic | CredentialPublic | ParameterPublic
  disabled?: boolean
  allowEdit?: boolean
  allowDelete?: boolean
}

const ActionsMenu = ({ type, value, disabled, allowEdit = true, allowDelete = true }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const deleteModal = useDisclosure()

  return (
    <>
      <Menu>
        <MenuButton
          isDisabled={disabled}
          as={Button}
          rightIcon={<BsThreeDotsVertical />}
          variant="unstyled"
        />
        <MenuList>
          {allowEdit && (
            <MenuItem
              onClick={editUserModal.onOpen}
              icon={<FiEdit fontSize="16px" />}
            >
              Edit {type}
            </MenuItem>
          )}

          {allowDelete && (
            <MenuItem
              onClick={deleteModal.onOpen}
              icon={<FiTrash fontSize="16px" />}
              color="ui.danger"
            >
              Delete {type}
            </MenuItem>
          )}


        </MenuList>
        {type === "User" && (
          <EditUser
            user={value as UserPublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        )}
        {type === "Item" && (
          <EditItem
            item={value as ItemPublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        )}

        {type === "Parameter" && (
          <EditParameter
            item={value as ParameterPublic}
            isOpen={editUserModal.isOpen}
            onClose={editUserModal.onClose}
          />
        )}
        <Delete
          type={type}
          id={"id" in value ? value.id : value.Name}
          isOpen={deleteModal.isOpen}
          onClose={deleteModal.onClose}
        />
      </Menu>
    </>
  )
}

export default ActionsMenu
